# Import necessary libraries
from flask import Flask, request, jsonify
import pandas as pd
# Import model from model.py
from model import PlayerSimilarityModel, FEATURE_COLS

# Initialize Flask
app = Flask(__name__)

# Load data and model
df = pd.read_csv("data/nba_combined_stats_bios_1996_2024.csv")
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