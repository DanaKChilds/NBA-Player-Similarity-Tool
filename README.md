# NBA Player Similarity Tool

This project is an interactive web application built using **Streamlit** and **Flask** that allows users to find NBA players with similar statistical profiles. It combines player biographical information and performance data from the NBA API (1996–2024) and uses cosine similarity via scikit-learn to compare players based on per-game statistics.

---

## Contents

- `/app.py`: Streamlit frontend for user interaction  
- `/api.py`: Flask backend providing a `/similar_players` endpoint  
- `/etl.py`: Script to download and merge player stats and bio data  
- `/model.py`: Player similarity model and utility functions  
- `/data/`: Contains the generated dataset  
- `requirements.txt`: Project dependencies  

---

## Data & Model

### Data Source

Data is gathered from the [`nba_api`](https://github.com/swar/nba_api) and covers:
- Seasons: **1996–2024**
- Stats: Points, rebounds, assists, blocks, steals, etc.
- Bios: Player age, team, headshots

### ETL Pipeline

The data pipeline is automated via etl.py, which:

Iterates over NBA seasons from 1996–2024

Retrieves per-game player statistics and bio info via the nba_api

Joins the two datasets on PLAYER_ID

Outputs a single, clean CSV for modeling:
```text
data/nba_combined_stats_bios_1996_2024.csv
```

Error handling is included to skip over unavailable player records. This ETL script can be run as a scheduled job or on-demand.

### Similarity Model

The similarity engine uses the `NearestNeighbors` model from `scikit-learn`, with cosine similarity on 12 statistical features:

- Points, Rebounds, Assists, Steals, Blocks, Turnovers  
- Three Pointers Attempted, Free Throws Attempted, Field Goal Percentage, Three Point Percetage, Usage Rate, True Shooting Percentage

Standard scaling is applied before fitting the model.

---

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/DanaKChilds/NBA-Player-Similarity-Tool.git
cd NBA-Player-Similarity-Tool
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Activate:
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## How to Use

### Step 1: Run the Flask API

```bash
python api.py
```

This starts the backend on:

```text
http://localhost:5000
```

### Step 2: Run the Streamlit App

In a new terminal:

```bash
streamlit run app.py
```

This opens the app at:

```text
http://localhost:8501
```

---

## Example API Call

```bash
curl -X POST http://localhost:5000/similar_players \
  -H "Content-Type: application/json" \
  -d '{
        "player": "Jayson Tatum",
        "season": "2022-23",
        "n": 5
      }'
```

### Response:

```json
[
  {
    "PLAYER_NAME_STATS": "Pascal Siakam",
    "SEASON": "2019-20",
    "AGE_STATS": 26,
    "TEAM_ABBREVIATION_STATS": "TOR",
    "similarity_score": 0.979
  }
]
```

---

## Deployment Options

The first option is to host the Streamlit frontend on [Streamlit Cloud](https://streamlit.io/cloud) and the Flask backend separately on a service like Render, Heroku, or AWS.

The second option would be to switch to a fully Streamlit-only deployment which would require moving the model logic from `api.py` into `app.py` and therefore bypassing Flask deployment.

---

## Acknowledgments

- [`nba_api`](https://github.com/swar/nba_api) for the API which allows for data collection for this project
- NBA headshots hosted via `cdn.nba.com`

---

## License

This project is released under the MIT License.
