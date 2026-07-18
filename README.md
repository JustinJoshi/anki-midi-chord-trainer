# Anki MIDI Chord Trainer

A two-tool setup for drilling chords on a MIDI keyboard with Anki integration. Use the **HTML app** for timed, repetitive practice sessions, or the **Python script** for hands-free Anki card reviews.

![Reflex Drill HTML App — top](./screenshot-1.png)

---

## What's in this repo

| File | What it is |
|------|-----------|
| `reflexDrillExt.html` | Standalone web app — blocked-practice chord drill with timer, stats, and AnkiConnect flip |
| `anki_midi_chord_trainer.py` | Python script — auto-checks your played chords against Anki cards during reviews |

---

## How the two tools work together

Both tools connect to **Anki** via [AnkiConnect](https://foosoft.net/projects/anki-connect/) and listen to your **MIDI keyboard**, but they serve different practice goals:

### `reflexDrillExt.html` — Blocked Practice Drill

Best for **speed and muscle-memory drilling** on a single chord or chord family.

- Open it in any browser (served locally via `python3 -m http.server`).
- Connect your MIDI keyboard and pick a chord (root + quality).
- Press **Start**, lift your hands, then play the chord as fast as you can.
- The timer starts the moment you release all keys and stops when you play the correct notes.
- Do **N reps** (8 / 12 / 16 / 20) per round. It tracks your **best single rep** and **best round average**.
- When you finish a round, it **automatically flips the current Anki card** so you can grade it.
- Modes:
  - **Single Shape** — drill one specific chord
  - **Family Cycle** — cycle through maj7 → 7 → m7 → m7b5 → dim7
  - **Extended Family** — include 9ths, 11ths, and 13ths
- Toggle **Show/Hide** chord notes if you want to test recognition vs. muscle memory.

### `anki_midi_chord_trainer.py` — Review Mode

Best for **actual Anki review sessions** where you want the computer to check your answer.

- Run the script while reviewing a deck in Anki.
- It reads the **correct chord notes** from the current card's field (configurable regex).
- Play the chord on your keyboard. After a short debounce, the script compares what you played vs. what's expected.
- **Correct** → flips the card so you can grade it (Again / Hard / Good / Easy).
- **Wrong** → prints which notes are missing or extra; try again.

### When to use which

| Goal | Tool |
|------|------|
| Drill one chord for speed | `reflexDrillExt.html` |
| Cycle through chord families | `reflexDrillExt.html` |
| Track rep times and PBs | `reflexDrillExt.html` |
| Review a structured Anki deck | `anki_midi_chord_trainer.py` |
| Let the computer grade your answer | `anki_midi_chord_trainer.py` |

---

## Requirements

| Component | Version / Notes |
|-----------|-----------------|
| Anki Desktop | 2.1.45+ (AnkiConnect requirement) |
| AnkiConnect | Add-on code `2055492159` |
| Python | 3.8+ (for the script) |
| MIDI keyboard | Any USB-MIDI device |
| Browser | Any modern browser with Web MIDI support (Chromium/Chrome/Firefox/Edge) |

---

## HTML App Setup

1. **Serve the file locally** (required for Web MIDI API):
   ```bash
   cd /path/to/this/repo
   python3 -m http.server 8766
   ```
2. Open `http://localhost:8766/reflexDrillExt.html` in your browser.
3. Click **Connect MIDI Keyboard** and allow MIDI access when prompted.
4. Select your chord settings and press **Start Drill**.

> **Tip:** You can also create a desktop shortcut / taskbar icon that auto-starts the server and opens the browser. See the launcher script in the repo history for an example.

---

## Python Script Setup

### Python dependencies

```bash
pip install mido python-rtmidi requests
```

### 1. Install AnkiConnect
- In Anki: `Tools > Add-ons > Get Add-ons...`
- Paste code: `2055492159`
- Restart Anki.

### 2. Prepare your note type
- Your note type needs a field containing the correct chord notes.
- By default the script reads the **Back** field and extracts notes with a regex.
- Example field content:
  ```
  Chord: C E G B  |  Scale: C Ionian (...)
  ```
- You can change `NOTES_FIELD` and `NOTES_PATTERN` in the script to match your own field layout.

### 3. Configure the script

Edit the top of `anki_midi_chord_trainer.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `NOTES_FIELD` | `"Back"` | Which card field contains the correct notes |
| `NOTES_PATTERN` | `r"Chord:\s*([A-Ga-g#b\s]+?)"` | Regex to extract the note list from that field |
| `MATCH_OCTAVE` | `False` | If `True`, the octave must match exactly; if `False`, only pitch class matters |
| `DEBOUNCE_SECONDS` | `0.35` | How long to wait after your last key-down before evaluating the chord |
| `ANKICONNECT_URL` | `http://127.0.0.1:8765` | AnkiConnect API endpoint |

### 4. Run

```bash
python anki_midi_chord_trainer.py
```

- Pick your MIDI input when prompted.
- Open a deck to review in Anki.
- Play chords on your keyboard.

---

## How the Python script works

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

---

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

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Web MIDI isn't supported in this browser" | Use Chromium, Chrome, Edge, or Firefox. Safari does not support Web MIDI. |
| "No MIDI input ports found" (Python script) | Plug in your keyboard and retry |
| "Not currently reviewing a card" | Make sure a review session is active in Anki |
| "Field 'Back' not found" | Check that your note type has the field configured in `NOTES_FIELD` |
| "Couldn't find a note list" | Adjust `NOTES_PATTERN` to match how your field stores chord notes |

---

## License

This is a personal utility project. Use and modify it however you like.
