import pytest
import pandas as pd
import requests
from model import PlayerSimilarityModel, FEATURE_COLS
from etl import get_combined_stats_and_bios_1996_onward

DATA_PATH = "data/nba_combined_stats_bios_1996_2024.csv"

# Test 1: ETL function
def test_etl_produces_data():
    df = get_combined_stats_and_bios_1996_onward()
    assert not df.empty, "ETL returned empty DataFrame"
    assert "PLAYER_ID" in df.columns
    assert "SEASON" in df.columns
    assert "PLAYER_NAME_STATS" in df.columns
    assert all(col in df.columns for col in FEATURE_COLS)

# Test 2: Similarity model
@pytest.fixture(scope="module")
def nba_data():
    return pd.read_csv(DATA_PATH)

def test_model_finds_similar_players(nba_data):
    model = PlayerSimilarityModel(nba_data)
    player = "LeBron James"
    season = "2020-21"

    if not ((nba_data["PLAYER_NAME_STATS"] == player) & (nba_data["SEASON"] == season)).any():
        pytest.skip(f"{player} not found in {season}")

    _, similar = model.find_similar(player, season, n=5)
    assert len(similar) == 5
    assert "similarity_score" in similar.columns
    assert similar["similarity_score"].between(0, 1).all()

# Test 3: API endpoint
def test_api_response_structure():
    payload = {
        "player": "Stephen Curry",
        "season": "2021-22",
        "n": 3
    }
    try:
        response = requests.post("http://localhost:5000/similar_players", json=payload)
    except requests.exceptions.ConnectionError:
        pytest.skip("API not running at localhost:5000")

    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
    assert len(result) == 3
    assert all("PLAYER_NAME_STATS" in r for r in result)
    assert all("similarity_score" in r for r in result)