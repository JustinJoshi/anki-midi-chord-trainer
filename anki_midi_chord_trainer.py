#!/usr/bin/env python3
"""
Anki MIDI Chord Trainer
========================
Play chords on a MIDI keyboard and have Anki auto-check your answer against
the correct notes stored on the current card, using AnkiConnect.

SETUP (one-time)
-----------------
1. In Anki: Tools > Add-ons > Get Add-ons... > paste code: 2055492159
   (this installs "AnkiConnect"). Restart Anki.
2. On your note type, make sure there's a field containing the correct notes
   for the chord, e.g. a field called "Notes" with content like:
       C,E,G          (pitch-class only, any octave — recommended)
   or  C4,E4,G4       (exact octave, if you set MATCH_OCTAVE = True below)
   Sharps: use '#' or 's' (C#, Cs). Flats: use 'b' (Eb).
3. pip install mido python-rtmidi requests
4. Run this script while Anki is open with a deck being reviewed:
       python anki_midi_chord_trainer.py

HOW IT WORKS
------------
- Listens to your MIDI input device.
- When you press and hold a chord, it waits until you stop adding new notes
  (DEBOUNCE_SECONDS) and then checks what's currently held against the
  correct-notes field on the card currently shown in Anki's reviewer.
- If correct: Anki flips to the answer (if not already shown). You then
  grade the card manually with Again/Hard/Good/Easy as normal.
- If wrong: prints what you played vs. what's expected, no card action —
  release all keys and try again.
"""

import time
import re
import sys

import mido
import requests

# ---------------------------------------------------------------------------
# CONFIG — edit these to match your setup
# ---------------------------------------------------------------------------
# Your deck is Basic (Front/Back). The correct notes live inside the Back
# field as text like: "Chord: C E G B  |  Scale: C Ionian (...)"
# NOTES_FIELD tells the script which field to read; NOTES_PATTERN pulls the
# note list out of that field's text. If you ever add a dedicated field
# (e.g. "Notes") just set NOTES_FIELD = "Notes" and NOTES_PATTERN = None.
NOTES_FIELD = "Back"
NOTES_PATTERN = re.compile(r"Chord:\s*([A-Ga-g#b\s]+?)(?:\s*\||$)")

MATCH_OCTAVE = False          # False = any octave counts (pitch-class match)
DEBOUNCE_SECONDS = 0.35       # how long to wait after your last key-down
ANKICONNECT_URL = "http://127.0.0.1:8765"

# ---------------------------------------------------------------------------
# Note-name <-> MIDI number helpers
# ---------------------------------------------------------------------------
PITCH_CLASSES = {
    "C": 0, "C#": 1, "DB": 1, "CS": 1,
    "D": 2, "D#": 3, "EB": 3, "DS": 3,
    "E": 4, "FB": 4,
    "F": 5, "F#": 6, "GB": 6, "FS": 6,
    "G": 7, "G#": 8, "AB": 8, "GS": 8,
    "A": 9, "A#": 10, "BB": 10, "AS": 10,
    "B": 11, "CB": 11,
}


def parse_note(token):
    """Parse 'C', 'C4', 'Eb3', 'F#5' etc. Returns (pitch_class, octave_or_None)."""
    token = token.strip().upper().replace("♯", "#").replace("♭", "B")
    m = re.match(r"^([A-G](?:#|B|S)?)(-?\d+)?$", token)
    if not m:
        raise ValueError(f"Can't parse note '{token}'")
    name, octave = m.group(1), m.group(2)
    if name not in PITCH_CLASSES:
        raise ValueError(f"Unknown note name '{name}'")
    pc = PITCH_CLASSES[name]
    return pc, (int(octave) if octave is not None else None)


def midi_to_pitch_class(note_num):
    return note_num % 12


def midi_to_pc_octave(note_num):
    # MIDI octave numbering where note 60 = C4
    return note_num % 12, (note_num // 12) - 1


def parse_expected(field_value):
    """Turn 'C,E,G' or 'C4,E4,G4' into a set of comparable identities."""
    tokens = [t for t in re.split(r"[,\s]+", field_value.strip()) if t]
    parsed = [parse_note(t) for t in tokens]
    if MATCH_OCTAVE:
        return {(pc, oct_) for pc, oct_ in parsed}
    return {pc for pc, _ in parsed}


def played_set(held_notes):
    if MATCH_OCTAVE:
        return {midi_to_pc_octave(n) for n in held_notes}
    return {midi_to_pitch_class(n) for n in held_notes}


def note_name(pc):
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return names[pc]


# ---------------------------------------------------------------------------
# AnkiConnect helpers
# ---------------------------------------------------------------------------
def ac_request(action, **params):
    payload = {"action": action, "version": 6, "params": params}
    r = requests.post(ANKICONNECT_URL, json=payload, timeout=5)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(f"AnkiConnect error on {action}: {data['error']}")
    return data["result"]


def get_current_card():
    """Returns the current reviewer card dict, or None if not reviewing."""
    try:
        return ac_request("guiCurrentCard")
    except RuntimeError:
        return None


def get_expected_notes(card):
    fields = card.get("fields", {})
    if NOTES_FIELD not in fields:
        raise RuntimeError(
            f"Field '{NOTES_FIELD}' not found on this note. "
            f"Available fields: {list(fields.keys())}"
        )
    raw = fields[NOTES_FIELD]["value"]
    # strip any HTML Anki may have added
    raw = re.sub(r"<[^>]+>", "", raw)

    if NOTES_PATTERN is not None:
        m = NOTES_PATTERN.search(raw)
        if not m:
            raise RuntimeError(
                f"Couldn't find a note list in the '{NOTES_FIELD}' field "
                f"using NOTES_PATTERN. Field text was: {raw!r}"
            )
        raw = m.group(1)

    return parse_expected(raw)


def show_answer_if_needed():
    ac_request("guiShowAnswer")


# ---------------------------------------------------------------------------
# MIDI listening loop
# ---------------------------------------------------------------------------
def pick_midi_port():
    ports = mido.get_input_names()
    if not ports:
        print("No MIDI input ports found. Plug in your keyboard and retry.")
        sys.exit(1)
    if len(ports) == 1:
        print(f"Using MIDI input: {ports[0]}")
        return ports[0]
    print("Available MIDI inputs:")
    for i, p in enumerate(ports):
        print(f"  [{i}] {p}")
    idx = input("Pick a port number: ").strip()
    return ports[int(idx)]


def main():
    port_name = pick_midi_port()
    held = set()
    last_event_time = None
    evaluated_this_chord = False

    print("\nReady. Play chords on your MIDI keyboard. Ctrl+C to quit.\n")

    with mido.open_input(port_name) as inport:
        while True:
            for msg in inport.iter_pending():
                if msg.type == "note_on" and msg.velocity > 0:
                    held.add(msg.note)
                    last_event_time = time.time()
                    evaluated_this_chord = False
                elif msg.type == "note_off" or (
                    msg.type == "note_on" and msg.velocity == 0
                ):
                    held.discard(msg.note)
                    if not held:
                        evaluated_this_chord = False  # reset for next attempt

            if (
                held
                and not evaluated_this_chord
                and last_event_time is not None
                and time.time() - last_event_time >= DEBOUNCE_SECONDS
            ):
                evaluated_this_chord = True
                check_chord(held)

            time.sleep(0.01)


def check_chord(held):
    card = get_current_card()
    if card is None:
        print("(Not currently reviewing a card in Anki — open a deck to review.)")
        return

    try:
        expected = get_expected_notes(card)
    except RuntimeError as e:
        print(f"⚠️  {e}")
        return

    got = played_set(held)

    if got == expected:
        print("✅ Correct chord!")
        try:
            show_answer_if_needed()
        except RuntimeError as e:
            print(f"(Card may already be showing the answer: {e})")
    else:
        if MATCH_OCTAVE:
            missing = expected - got
            extra = got - expected
        else:
            missing = {note_name(pc) for pc in expected - got}
            extra = {note_name(pc) for pc in got - expected}
        print(f"❌ Not quite. Missing: {sorted(missing) or '—'}  Extra: {sorted(extra) or '—'}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")
