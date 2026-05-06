<div align="center">
  <img src="https://skidding.dev/content/cdn/RJXNtelWtEcr.png" alt="Pocketfish Logo" width="100"/>

  # Pocketfish

  **Real time chess bot for chess.com, powered by Stockfish**

  ![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
  ![PyQt5](https://img.shields.io/badge/PyQt5-GUI-41CD52?style=flat&logo=qt&logoColor=white)
  ![Stockfish](https://img.shields.io/badge/Engine-Stockfish-orange?style=flat)
  ![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat&logo=windows&logoColor=white)

  <img src="https://skidding.dev/content/cdn/vIQSeloupioy.gif" alt="Pocketfish in action" width="680"/>

</div>

---

Pocketfish watches your screen, finds the chess board, tracks every move, and draws the best move suggestion right on your display. No browser extensions, no injected scripts, nothing that touches chess.com at all.

## What it does

Pocketfish uses computer vision to detect and read the board in real time. Once it knows the position it runs Stockfish in the background and overlays an arrow on screen showing exactly where to move. Everything happens locally, the only thing on screen is a transparent window sitting on top of your browser.

It also handles things like orientation detection (so it works whether you're playing white or black), automatic re sync if the board drifts out of state, and a move log so you can follow along with what it detected.

## Features

- Automatically finds the chess board across any monitor
- Draws a move arrow directly on screen with no browser interaction
- Full Stockfish UCI support with configurable depth, time, skill, threads and hash
- Detects board orientation automatically when you switch sides
- Strength presets ranging from ~1200 Elo all the way to near perfect master play
- Live eval bar and mini board view inside the control panel
- Move log showing every move played and who played it

## Installation
 
You'll need Python 3.8 or newer. That's it.
 
1. Download or clone the repo
2. Run `setup.bat`
That's it. The setup script installs all Python dependencies and downloads the Stockfish engine automatically. When it's done it creates a `start.bat` in the same folder and removes itself.
 
From then on just double click `start.bat` to launch Pocketfish.
 
> If you get a Python not found error, make sure Python is installed and added to your PATH. You can grab it from [python.org](https://www.python.org/downloads/).

**Dependencies**

```
PyQt5
chess
mss
opencv-python
numpy
dexvstuff
```

## Usage

```bash
python pocketfish.py
```

Pick your side and tweak the engine settings in the startup dialog, then hit Start. Open chess.com, start a game, and the move arrow will appear on screen automatically. You can adjust everything live from the control panel without restarting.

## Strength presets

The presets are designed around how detectable the play looks, not just how strong it is. Lower settings introduce natural inaccuracies so the game looks human. Master plays nearly perfectly and will almost certainly flag anticheat.

| Preset | Elo | Accuracy | Notes |
|--------|-----|----------|-------|
| Beginner | ~1200 | 65–72% | Very human, safe to use |
| Casual | ~1550 | 75–82% | Makes some mistakes |
| Club | ~1850 | 82–87% | Best balance for online play |
| Strong | ~2150 | 87–92% | Getting borderline |
| Master | ~2850 | 95%+ | Will likely flag anticheat |

## How it works

Every 120ms Pocketfish grabs a screenshot of the region where the board was found and classifies each of the 64 squares as empty, white piece, or black piece based on pixel brightness and corner color. It diffs the result against the previous frame, scores all legal moves against the observed changes, and picks the one that best explains what it sees.

If the board drifts out of sync (premoves, lag, a move it missed) it runs a 1 to 3 ply search through legal positions to find the closest match and snaps back automatically.

Once the position is known, Stockfish analyses it and the best move gets drawn on screen through a transparent always on top window.

## Project structure

```
pocketfish/
├── assets/
│   ├── logo.png
│   └── stockfish.exe
├── main.py          entry point, connects all the signals and threads
├── config.py        constants and default values
├── worker.py        background thread running the capture and state loop
├── engine.py        Stockfish wrapper using python-chess
├── vision.py        board detection and square classification with OpenCV
├── moves.py         move inference and board re-sync logic
├── overlay.py       transparent screen overlay that draws the move arrow
├── panel.py         control panel UI
├── startup.py       startup dialog
├── widgets.py       BoardView and EvalBar custom widgets
└── style.py         dark theme stylesheet
```

## License

MIT — see [LICENSE](https://github.com/dexvnd/pocketfish/LICENSE) for details.

---

<div align="center">
  <sub>Built with PyQt5, python-chess, OpenCV and Stockfish</sub>
</div>