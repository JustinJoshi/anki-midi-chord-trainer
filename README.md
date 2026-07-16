# Anki MIDI Chord Trainer

Use a MIDI keyboard to answer Anki flashcards during reviews. The script listens to your keyboard, compares the chord you play against the correct notes stored on the current card, and automatically flips the card when you get it right. You keep full control over grading the card afterwards.

## What it does

- Connects to Anki via [AnkiConnect](https://foosoft.net/projects/anki-connect/) over a local HTTP API.
- Listens to a MIDI input device in real time.
- When you hold a chord steady for a short debounce period, it checks your played notes against the card's expected notes.
- If the notes match, it reveals the answer side of the card so you can review it and choose **Again / Hard / Good / Easy** yourself.
- If the notes don't match, it tells you what's missing or extra, and you can try again.

## Requirements

| Component | Version / Notes |
|-----------|-----------------|
| Anki Desktop | 2.1.45+ (AnkiConnect requirement) |
| AnkiConnect | Add-on code `2055492159` |
| Python | 3.8+ |
| MIDI keyboard | Any USB-MIDI device |

## Python dependencies

```bash
pip install mido python-rtmidi requests
```

## Setup

1. **Install AnkiConnect**
   - In Anki: `Tools > Add-ons > Get Add-ons...`
   - Paste code: `2055492159`
   - Restart Anki.

2. **Prepare your note type**
   - Your note type needs a field containing the correct chord notes.
   - By default the script reads the **Back** field and extracts notes with a regex.
   - Example field content:
     ```
     Chord: C E G B  |  Scale: C Ionian (...)
     ```
   - You can change `NOTES_FIELD` and `NOTES_PATTERN` in the script to match your own field layout.

3. **Configure the script** (edit the top of `anki_midi_chord_trainer.py`)

   | Variable | Default | Description |
   |----------|---------|-------------|
   | `NOTES_FIELD` | `"Back"` | Which card field contains the correct notes |
   | `NOTES_PATTERN` | `r"Chord:\s*([A-Ga-g#b\s]+?)"` | Regex to extract the note list from that field |
   | `MATCH_OCTAVE` | `False` | If `True`, the octave must match exactly; if `False`, only pitch class matters |
   | `DEBOUNCE_SECONDS` | `0.35` | How long to wait after your last key-down before evaluating the chord |
   | `ANKICONNECT_URL` | `http://127.0.0.1:8765` | AnkiConnect API endpoint |

4. **Run**
   ```bash
   python anki_midi_chord_trainer.py
   ```
   - Pick your MIDI input when prompted.
   - Open a deck to review in Anki.
   - Play chords on your keyboard.

## How it works

### MIDI input loop

The script uses `mido` to open your MIDI input port and polls for `note_on` / `note_off` messages. It tracks which notes are currently held in a `set`. When the set stabilizes for `DEBOUNCE_SECONDS`, the chord is evaluated.

### Note matching

- Your played MIDI note numbers are converted to **pitch classes** (0–11) or to **(pitch class, octave)** pairs depending on `MATCH_OCTAVE`.
- The expected notes are parsed from the card field using the configured regex and converted the same way.
- The two sets are compared. If they are identical, the chord is correct.

### AnkiConnect actions

| Action | What it does |
|--------|-------------|
| `guiCurrentCard` | Fetches the card currently being reviewed |
| `guiShowAnswer` | Flips the card to the answer side |

The script **does not** call `guiAnswerCard`. After the answer is revealed, you manually press `1`–`4` (or click the buttons) to grade the card as usual.

### Error reporting

If your played notes don't match, the script prints:

```
❌ Not quite. Missing: [D, F]  Extra: [A#]
```

This helps you adjust your fingering before trying again.

## Card format

The script expects note names separated by commas or spaces. Supported syntax:

- Pitch class only (recommended when `MATCH_OCTAVE = False`):
  ```
  C, E, G, B
  ```
- With octave (when `MATCH_OCTAVE = True`):
  ```
  C4, E4, G4, B4
  ```
- Accidentals: `#` or `s` for sharps, `b` for flats (e.g. `Eb`, `F#`, `Gs`)

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "No MIDI input ports found" | Plug in your keyboard and retry |
| "Not currently reviewing a card" | Make sure a review session is active in Anki |
| "Field 'Back' not found" | Check that your note type has the field configured in `NOTES_FIELD` |
| "Couldn't find a note list" | Adjust `NOTES_PATTERN` to match how your field stores chord notes |

## License

This is a personal utility script. Use and modify it however you like.
