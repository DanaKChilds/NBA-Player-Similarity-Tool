
# NBA Player Similarity Tool

This project is an interactive web application built using Streamlit and Flask that allows users to find NBA players with similar statistical profiles. It combines player biographical information and performance data from the NBA API (1996–2024) and uses cosine similarity via scikit-learn to compare players based on per-game statistics.

## Contents

- `/app.py`: Streamlit frontend for user interaction
- `/api.py`: Flask backend providing a `/similar_players` endpoint
- `/etl.py`: Script to download and merge player stats and bio data using Prefect
- `/model.py`: Player similarity model and utility functions
- `email_credentials.py`: Script to configure email alert block for Prefect
- `requirements.txt`: Project dependencies

## Data & Model

### Data Source

Data is gathered from the nba_api and covers:

- **Seasons**: 1996–2024
- **Stats**: Points, rebounds, assists, blocks, steals, etc.
- **Bios**: Player age, team, headshots

### ETL Pipeline

The data pipeline is built using Prefect and is scheduled to run monthly via a local process work pool. The steps are:

1. Iterate over NBA seasons from 1996–2024
2. Retrieve per-game player statistics and bio info
3. Join the two datasets on `PLAYER_ID`
4. Output a clean dataset as:
   - `nba_player_data.db` (SQLite table: `player_stats`)
   - `data/nba_combined_stats_bios_1996_2024.csv` (only for manual data inspection)

Error handling is built into the pipeline.

### Similarity Model

The similarity engine uses the NearestNeighbors model from scikit-learn, with cosine similarity on 12 statistical features:

- Points, Rebounds, Assists, Steals, Blocks, Turnovers
- Three Pointers Attempted, Free Throws Attempted, Field Goal %, Three Point %, Usage Rate, True Shooting %

Standard scaling is applied before fitting the model.

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

### 4. Run the ETL Pipeline (First Time Only)

You must generate the initial dataset before using the app. This pulls NBA player stats and bios and saves them to `nba_player_data.db` and `data/nba_combined_stats_bios_1996_2024.csv`:

```bash
python etl.py
```

> Note: You only need to run this once unless you want to refresh the data manually later.

## Running the App

### Step 1: Run the Flask API

```bash
python api.py
```

### Step 2: Run the Streamlit App (new terminal)

```bash
streamlit run app.py
```

### Step 3: Interact with the App

Once the app is running:

1. Use the dropdown menu to select a player or type in a player's name.
2. Choose a specific season for that player.
3. Use the slider to select how many similar players to return (1–10).
4. Click **"Find Similar Players"**.
5. The app will display:
   - The selected player's headshot, team, age, and stats
   - A list of most similar players with matching info and similarity scores

Note: The App will not return a season from the selected player as a similar player.

The Flask API must be running on port 5000 for the Streamlit app to work properly.

---

## Automating the ETL with Prefect (only if regular updates required, otherwise skip)

### Step 1: Configure Email Alerts

Open `email_credentials.py` and replace the placeholder values with your actual email address and an app-specific password:

```python
your_email = "youremail@gmail.com"
your_app_password = "your_app_password"
```

> Note: Use an app-specific password (e.g., from Gmail), not your regular email password.

Then run the script to save the credentials securely:

```bash
python email_credentials.py
```

This stores credentials as a Prefect block that the ETL pipeline can access.

### Step 2: Start the local Prefect server

```bash
prefect server start
```

Leave this terminal running.

### Step 3: Set API URL (new terminal)

```powershell
$env:PREFECT_API_URL = "http://127.0.0.1:4200/api"
```

### Step 4: Create a work pool

```bash
prefect work-pool create --type process local-pool
```

### Step 5: Deploy the ETL job

```bash
prefect deploy etl.py:nba_etl_pipeline --name "monthly-nba-etl" --cron "0 7 1 * *" --pool local-pool --work-queue default
```

### Step 6: Start the worker in the project folder

Be sure to start the worker from the project root (`NBA-Player-Similarity-Tool`) so output files are written to the correct location.

```bash
prefect worker start -p local-pool -q default
```

### Step 7: Test it manually (optional)

In a new terminal run: 

```bash
prefect deployment run "NBA ETL Pipeline/monthly-nba-etl"

```

## Example API Call

```bash
curl -X POST http://localhost:5000/similar_players   -H "Content-Type: application/json"   -d '{
        "player": "Jayson Tatum",
        "season": "2022-23",
        "n": 5
      }'
```

**Response:**

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

## Deployment Options

- Host the Streamlit frontend on Streamlit Cloud and host Flask backend on Render or Heroku.
- Merge backend logic into Streamlit for unified deployment

## Acknowledgments

- `nba_api` for player data
- `cdn.nba.com` for player headshots

## License

MIT License
