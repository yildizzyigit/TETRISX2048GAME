# 🎮 Tetris 2048

A hybrid game that combines the falling piece mechanics of **Tetris** with the number-merging gameplay of **2048**, built with Python.

---

## 🕹️ Gameplay

Tetris pieces fall onto the grid — but each tile carries a number. When two tiles with the same number land next to each other in the same column, they merge and double in value, just like in 2048. Reach the **2048 tile** to win!

- Pieces fall and lock onto the grid
- Matching adjacent tiles merge automatically (chain merges supported)
- Floating tiles after a merge are cleared and added to your score
- Fill a complete row to clear it and earn bonus points
- The game speeds up as your score increases

---

## ✨ Features

- 🔢 **2048 merging mechanic** — column-wise chain merging after every piece lands
- 👻 **Ghost piece** — shows where the current piece will land
- 🔄 **Wall kick** — rotation near walls attempts ±1, ±2 horizontal adjustments
- 📦 **Hold system** — press `C` to save a piece for later (once per piece)
- 🎨 **4 themes** — Classic, Dark, Ocean, Forest (saved between sessions)
- 🏆 **High score** — persisted to disk across sessions
- 🎵 **Sound effects** — merge, line clear, win, and game over sounds
- 📈 **Dynamic difficulty** — speed increases every 200 points

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| `← →` | Move left / right |
| `↑` | Rotate |
| `↓` | Soft drop |
| `Space` | Hard drop |
| `C` | Hold |
| `P` | Pause / Resume |
| `R` | Restart |

---

## 🗂️ Project Structure

```
Tetris_2048/
├── Tetris_2048.py     # Entry point — game loop, menus, input handling
├── game_grid.py       # GameGrid class — all game logic (merge, clear, BFS)
├── tetromino.py       # Tetromino class — movement, rotation, hard drop
├── tile.py            # Tile class — number tiles with 2048 color palette
├── point.py           # Point class — 2D coordinate helper
├── lib/               # Graphics library (stddraw, color, picture)
├── sounds/            # Sound effects and background music
├── images/            # Menu image
├── high_score.txt     # Persisted high score
└── theme.txt          # Persisted theme selection
```

---

## ⚙️ How It Works

When a piece lands, the game runs these steps in order:

1. **Lock** — tiles are written into the grid
2. **Merge** (`_merge_tiles`) — columns are scanned bottom-to-top; equal adjacent tiles merge and chain
3. **Free tile cleanup** (`_handle_free_tiles`) — BFS from the bottom row removes floating tiles
4. **Line clear** (`_clear_full_lines`) — full rows are cleared with a rainbow animation
5. **Win check** — any tile reaching 2048 triggers the win screen

---

## 🚀 Requirements

- Python 3.x
- NumPy
- Pygame

Install dependencies:

```bash
pip install numpy pygame
```

Run the game:

```bash
python Tetris_2048.py
```

---

## 👥 Authors

> Yiğit Yıldız

---

## 📄 License

This project was developed as an academic assignment.
