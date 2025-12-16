# Human Baseline for Atari Breakout
This project implements a human-playable version of the ALE (Arcade Learning Environment) Breakout game. Its primary purpose is to establish a **human baseline** for Reinforcement Learning (RL) comparisons.

It maps standard keyboard inputs to the ALE environment actions, ensuring a fair comparison between human performance and AI agents operating in the same environment constraints.

## Features
- **ALE Integration**: Plays directly against the Gymnasium `ALE/Breakout-v5` environment.
- **Step Limits**: Run for a fixed number of steps (standardized testing) or infinite free play.
- **Leaderboard**: 
    - Persistent CSV-based leaderboard (`scores/leaderboard.csv`).
    - Tracks Top 10 high scores.
    - Calculates and displays the human average (baseline).
    - Supports tied ranking (e.g., 1st, 1st, 3rd).
- **Game Over Screen**: Interactive screen to enter player name, view stats, and relaunch/quit.

## Installation
1. **Clone the repository**.
2. **Create a virtual environment** (optional but recommended):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```
3. **Install Dependencies**:
    Ensure you have Python 3.10+ installed. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
Run the game using Python:
```bash
python human_baseline.py
```

### Controls
| Key | Action |
| :--- | :--- |
| **Space** | FIRE (Start Game / Launch Ball) |
| **Left Arrow** / **A** | Move Left |
| **Right Arrow** / **D** | Move Right |

### Command Line Arguments
- `--steps <int>`: Set a maximum number of steps for the episode. Default is `-1` (Infinite / Free Play).
  - Example: `python human_baseline.py --steps 1000` (Play for strictly 1000 frames).

## Leaderboard
Scores are automatically saved to `scores/leaderboard.csv` upon completion of a game (after name entry). 
The game displays:
- **Your Rank & Score**: e.g., "#1 Player - 50"
- **Human Average**: The mean score of all recorded games.
- **Top 10**: The highest scores achieved.
