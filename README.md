# Anki MIDI Chord Trainer

A multi-tool setup for drilling chords and progressions on a MIDI keyboard with Anki integration. Use the **HTML apps** for timed, repetitive practice sessions, or the **Python script** for hands-free Anki card reviews.

![Reflex Drill HTML App — top](./screenshot-1.png)

---

## What's in this repo

| File | What it is |
|------|-----------|
| `reflexDrillExt.html` | Main web app — blocked-practice chord drill with timer, stats, AnkiConnect flip, and optional time-based auto-grading. Includes **Welcome** and **Chord Drill** tabs, plus a link to the Progression Drill. |
| `progression-drill.html` | Companion web app — ii-V-I and 12-bar blues progression drill with loop timing. Shares the same top navigation bar so it feels like part of the same site. |
| `anki_midi_chord_trainer.py` | Python script — auto-checks your played chords against Anki cards during reviews |

---

## How the two tools work together

All tools listen to your **MIDI keyboard**, but they serve different practice goals:

### `reflexDrillExt.html` — Blocked Practice Drill

Best for **speed and muscle-memory drilling** on a single chord or chord family.

- Open it in any browser (served locally via `python3 -m http.server`).
- Use the **Welcome** tab to read the landing page, the **Chord Drill** tab to use the drill, or the **Progression** link to switch to the progression drill.
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
- **Anki Sync** — turn on "Follow card" and the app polls AnkiConnect for the current review card. When the card changes, the app parses the chord on the front (e.g. `Gm7`, `Cmaj7`, `F#m9(maj7)`) and automatically selects it for you.
- **Automatic Timer** — when Anki Sync is following a card, a new card automatically triggers a countdown and starts the drill hands-free.
  - The countdown length is editable (default 3 s) and persists across sessions.
  - **Hide until go** masks the big chord symbol and the Anki Sync status line during the countdown, then reveals them the instant the timer starts.
- **Break Before Grading** — after a round finishes, optionally wait a configurable number of seconds before flipping/grading the Anki card.
  - Shows a visible "Grading in N…" countdown in the complete box.
  - A bell toggle next to the break-seconds field enables or mutes the ticking sound during that countdown.
  - Hitting **Redo**, **Next chord**, or **Stop** mid-break cancels the countdown so the app never grades a card you've already moved past.
- **Auto-Grade** — when a round finishes, the app flips the Anki card and can automatically submit a grade based on your first-chord reaction time:
  - **Good** if under the "good" threshold (default 2.0 s)
  - **Hard** if under the "hard" threshold (default 4.0 s)
  - **Again** otherwise
  - A persistent grade status badge next to the Auto-Grade toggle shows **No grade sent yet** → **Sending to Anki…** → **Last sent: Good (1.42 s)** and stays on screen until the next grade actually replaces it.
  - Thresholds, break seconds, countdown seconds, and the break-countdown tick-sound preference all persist across sessions. The Auto-Grade, Automatic Timer, Hide-until-go, and Anki Sync toggles themselves reset to off on reload so nothing auto-grades or auto-hides silently.

### `progression-drill.html` — Progression Drill

Best for **moving between chords smoothly** in a harmonic context, not just one chord at a time.

- Open it from the **Progression** link in `reflexDrillExt.html`, or directly in any browser (served locally via `python3 -m http.server`).
- Connect your MIDI keyboard and pick a **progression** and **key**:
  - **ii-V-I** — cycle through ii → V → I (e.g. Dm7 → G7 → Cmaj7 in C)
  - **12-Bar Blues** — standard blues form in the chosen key
- Press **Start Loop**, lift your hands, then play each chord in the sequence as it appears.
- The timer tracks each **individual chord transition**.
- After you hit the last chord, the loop **auto-restarts** so you can keep going.
- Tracks **loop count**, **best single transition**, and **best loop average**.
- Shows the **matching scale** for your right hand (Dorian for m7, Mixolydian for dom7, Ionian for maj7).
- Uses Tone.js for audio chimes on each correct chord and loop completion.

**How to practice with it:**
1. Start with left hand only — comp the chords as block chords, focusing on smooth motion between shapes.
2. Add the right hand — run the scale shown for each chord, switching the instant the chord changes.
3. Loop with a metronome at slow tempo, increase only when clean.
4. Cycle through keys (C, G, D, A, E) using the same process.
5. Add the 12-Bar Blues alongside ii-V-I for a second harmonic vehicle.
6. Finally, practice against real backing tracks for tempo and time-feel.

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
| Practice ii-V-I transitions | `progression-drill.html` |
| Practice 12-bar blues form | `progression-drill.html` |
| Loop progressions with timing | `progression-drill.html` |
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

Both HTML apps need to be served locally for Web MIDI to work.

1. **Serve the files locally**:
   ```bash
   cd /path/to/this/repo
   python3 -m http.server 8766
   ```
2. Open the main app in your browser:
   - `reflexDrillExt.html` has **Welcome**, **Chord Drill**, and a **Progression** link.
   - You can also open the progression drill directly at `http://localhost:8766/progression-drill.html`; the same navigation bar links back to the main app.
3. Click **Connect MIDI Keyboard** and allow MIDI access when prompted.
4. (Optional) Turn on **Anki Sync → Follow card** to have the app auto-select the chord shown on Anki's current card.
5. Select your settings and press **Start**.

> **Tip:** You can also create desktop shortcuts / taskbar icons that auto-start the server and open the browser. See the launcher scripts below.

### Anki Sync card format

When **Follow card** is enabled, the app reads the rendered front of the current Anki review card via AnkiConnect and looks for a chord symbol. Supported examples:

- `Gm7`, `Cmaj7`, `F#m9(maj7)`, `Bbmaj9`, `A13#11`, `Eb7b9`
- Sharps are mapped to their enharmonic flat roots (`C#m7` becomes `Dbm7`).

If the card front doesn't contain a recognizable chord, the status line will say "Card found, no chord parsed".

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
| `guiAnswerCard` | Submits a grade (ease 1–4) for the revealed card |

The Python script **does not** call `guiAnswerCard`. After the answer is revealed, you manually press `1`–`4` (or click the buttons) to grade the card as usual.

`reflexDrillExt.html` uses `guiAnswerCard` only when **Auto-Grade** is enabled and the drill is actively following a specific Anki card.

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

## Desktop / Taskbar Launchers

You can create `.desktop` entries so these apps open from your app menu or taskbar like native programs. The launcher scripts below start a local HTTP server, wait until it is actually serving the file, and then open the app in a new Firefox window with a cache-busting URL so Firefox always loads the latest version.

### Reflex Drill launcher

Save to `~/.local/bin/reflex-drill-launch`:

```bash
#!/bin/bash
set -e

DIR="/home/justin/reflex-drill"
PORT=8766
CACHE_BUST=$(date +%s)
BASE_URL="http://127.0.0.1:$PORT/reflexDrillExt.html"
URL="$BASE_URL?v=$CACHE_BUST"
LOG="/tmp/reflex-drill-launch.log"

exec > >(tee -a "$LOG") 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Launching Reflex Drill..."

pkill -f "python3 -m http.server $PORT" 2>/dev/null || true
sleep 0.2

cd "$DIR"
python3 -m http.server "$PORT" &
SERVER_PID=$!
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Started server (PID $SERVER_PID) on port $PORT"

READY=false
for i in {1..50}; do
  if curl -s -o /dev/null -w "%{http_code}" "$URL" | grep -q "^200$"; then
    READY=true
    break
  fi
  sleep 0.1
done

if [ "$READY" != "true" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: server did not become ready on $URL" >&2
  exit 1
fi

firefox --new-window "$URL" &
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Reflex Drill launched."
```

Create `~/.local/share/applications/reflex-drill.desktop`:

```ini
[Desktop Entry]
Name=Reflex Drill
Comment=Blocked Chord Drill — MIDI & Anki
Exec=/home/justin/.local/bin/reflex-drill-launch
Icon=reflex-drill
Type=Application
Categories=AudioVideo;Audio;Education;Music;
StartupNotify=true
Terminal=false
```

### Progression Drill launcher

Save to `~/.local/bin/progression-drill-launch`:

```bash
#!/bin/bash
set -e

DIR="/home/justin/reflex-drill"
PORT=8767
CACHE_BUST=$(date +%s)
BASE_URL="http://127.0.0.1:$PORT/progression-drill.html"
URL="$BASE_URL?v=$CACHE_BUST"
LOG="/tmp/progression-drill-launch.log"

exec > >(tee -a "$LOG") 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Launching Progression Drill..."

pkill -f "python3 -m http.server $PORT" 2>/dev/null || true
sleep 0.2

cd "$DIR"
python3 -m http.server "$PORT" &
SERVER_PID=$!
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Started server (PID $SERVER_PID) on port $PORT"

READY=false
for i in {1..50}; do
  if curl -s -o /dev/null -w "%{http_code}" "$URL" | grep -q "^200$"; then
    READY=true
    break
  fi
  sleep 0.1
done

if [ "$READY" != "true" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: server did not become ready on $URL" >&2
  exit 1
fi

firefox --new-window "$URL" &
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Progression Drill launched."
```

Create `~/.local/share/applications/progression-drill.desktop`:

```ini
[Desktop Entry]
Name=Progression Drill
Comment=ii-V-I and 12-bar blues MIDI drill
Exec=/home/justin/.local/bin/progression-drill-launch
Icon=progression-drill
Type=Application
Categories=AudioVideo;Audio;Education;Music;
StartupNotify=true
Terminal=false
```

Finally, register the entries:

```bash
chmod +x ~/.local/bin/reflex-drill-launch ~/.local/bin/progression-drill-launch
update-desktop-database ~/.local/share/applications
```

If a launcher ever seems to do nothing, check its log file (`/tmp/reflex-drill-launch.log` or `/tmp/progression-drill-launch.log`) for the exact error.

## License

This is a personal utility project. Use and modify it however you like.
