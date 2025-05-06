# Import necessary libraries
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

# Define features used in model
FEATURE_COLS = [
    'PTS_STATS', 'REB_STATS', 'AST_STATS', 'STL', 'BLK', 'TOV',
    'FG3A', 'FTA', 'FG3_PCT', 'FG_PCT', 'USG_PCT', 'TS_PCT'
]

# Rename columns for better readability
DISPLAY_LABELS = {
    "PTS_STATS": "Points Per Game",
    "REB_STATS": "Rebounds Per Game",
    "AST_STATS": "Assists Per Game",
    "STL": "Steals Per Game",
    "BLK": "Blocks Per Game",
    "TOV": "Turnovers Per Game",
    "FG3A": "Three Point Field Goals Attempted Per Game",
    "FTA": "Free Throws Attempted Per Game",
    "FG3_PCT": "Three Point Field Goal Percentage",
    "FG_PCT": "Field Goal Percentage",
    "USG_PCT": "Usage Rate",
    "TS_PCT": "True Shooting Percentage"
}

# Define model class for player similarity
class PlayerSimilarityModel:
    def __init__(self, dataframe, feature_cols=FEATURE_COLS, id_col="PLAYER_NAME_STATS", season_col="SEASON"):
        self.df = dataframe.dropna(subset=feature_cols).copy()
        self.feature_cols = feature_cols
        self.id_col = id_col
        self.season_col = season_col
# Scale features and fit NearestNeighbors model
        self.scaler = StandardScaler()
        self.model = NearestNeighbors(metric="cosine")
        features = self.scaler.fit_transform(self.df[feature_cols])
        self.model.fit(features)

# Function to find similar players
    def find_similar(self, player_name, season, n=5):
        mask = (self.df[self.id_col] == player_name) & (self.df[self.season_col] == season)
# Error handling
        if not mask.any():
            raise ValueError(f"{player_name} not found in season {season}")
# Define player vector and find nearest neighbors
        player_vector = self.scaler.transform(self.df.loc[mask, self.feature_cols])
        distances, indices = self.model.kneighbors(player_vector, n_neighbors=n + 10)
# Retrieve similar players and compute similarity scores
        result_df = self.df.iloc[indices[0]].copy()
        result_df["similarity_score"] = 1 - distances[0]
# Exclude the original player from the results
        filtered = result_df[result_df[self.id_col] != player_name].head(n)
# Format and return the results
        query_stats = self.df.loc[mask, ["PLAYER_ID", self.id_col, self.season_col, "AGE_STATS", "TEAM_ABBREVIATION_STATS"] + self.feature_cols]
        return query_stats, filtered[["PLAYER_ID", self.id_col, self.season_col, "AGE_STATS", "TEAM_ABBREVIATION_STATS", "similarity_score"] + self.feature_cols]

# Function to add headshot URLs to the dataframe
def add_headshot_column(df):
    df["HEADSHOT"] = df["PLAYER_ID"].apply(lambda pid: f"https://cdn.nba.com/headshots/nba/latest/260x190/{pid}.png")
    return df