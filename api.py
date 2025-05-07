# Import necessary libraries
from flask import Flask, request, jsonify
import pandas as pd
import sqlite3
# Import model from model.py
from model import PlayerSimilarityModel, FEATURE_COLS

# Initialize Flask
app = Flask(__name__)

# Load data from SQLite database and model
conn = sqlite3.connect("nba_player_data.db")
df = pd.read_sql("SELECT * FROM player_stats", conn)
conn.close()

model = PlayerSimilarityModel(df, FEATURE_COLS)

# Definel API endpoint
@app.route("/similar_players", methods=["POST"])
def similar_players():
    data = request.get_json()
    player = data.get("player")
    season = data.get("season")
    n = data.get("n", 5)

    if not player or not season:
        return jsonify({"error": "Both 'player' and 'season' are required."}), 400

    try:
        _, similar = model.find_similar(player, season, n=n)
        return jsonify(similar.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)