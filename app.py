# Import necessary libraries
import streamlit as st
import pandas as pd
import requests
# Import model from model.py
from model import FEATURE_COLS, DISPLAY_LABELS, add_headshot_column

# Cache loading of CSV file
@st.cache_data
def load_data():
    return pd.read_csv("data/nba_combined_stats_bios_1996_2024.csv")

# Load player data
df = load_data()

# Set up user inputs and display
st.title("NBA Player Similarity Tool")
player_options = sorted(df["PLAYER_NAME_STATS"].unique())
selected_player = st.selectbox("Select a player", player_options)
season_options = sorted(df[df["PLAYER_NAME_STATS"] == selected_player]["SEASON"].unique(), reverse=True)
selected_season = st.selectbox("Select a season", season_options)
n_neighbors = st.slider("How many similar players?", 1, 10, 5)

# Add button to initiate query to Flask API
if st.button("Find Similar Players"):
    try:
        response = requests.post(
            "http://localhost:5000/similar_players",
            json={"player": selected_player, "season": selected_season, "n": n_neighbors}
        )

        if response.status_code == 200:
            similar = pd.DataFrame(response.json())
            query_stats = df[(df["PLAYER_NAME_STATS"] == selected_player) & (df["SEASON"] == selected_season)]
            query_stats = add_headshot_column(query_stats)
            similar = add_headshot_column(similar)
        else:
            st.error(f"API Error: {response.json().get('error', 'Unknown error')}")
            st.stop()

# Display statistics for selected player
        st.subheader("Selected Player Stats")
        for _, row in query_stats.iterrows():
            cols = st.columns([1, 3])
            with cols[0]:
                st.image(row["HEADSHOT"], width=75)
            with cols[1]:
                st.markdown(f"**{row['PLAYER_NAME_STATS']}** ({row['SEASON']})")
                st.markdown(f"Team: `{row['TEAM_ABBREVIATION_STATS']}`")
                st.markdown(f"Age: `{int(row['AGE_STATS'])}`")

            sub_stats = {DISPLAY_LABELS.get(col, col): row[col] for col in FEATURE_COLS}
            stats_df = pd.DataFrame([sub_stats])
            st.dataframe(stats_df, hide_index=True)

# Display statistics for similar players
        st.subheader("Most Similar Players")
        for _, row in similar.iterrows():
            cols = st.columns([1, 3])
            with cols[0]:
                st.image(row["HEADSHOT"], width=75)
            with cols[1]:
                st.markdown(f"**{row['PLAYER_NAME_STATS']}** ({row['SEASON']})")
                st.markdown(f"Team: `{row['TEAM_ABBREVIATION_STATS']}`")
                st.markdown(f"Age: `{int(row['AGE_STATS'])}`")
                st.markdown(f"Similarity score: `{row['similarity_score']:.3f}`")
# Display only desired columns
            sub_stats = row[FEATURE_COLS].copy()
            sub_stats.index = [DISPLAY_LABELS.get(idx, idx) for idx in sub_stats.index]
            stats_df = pd.DataFrame(sub_stats).T
            st.dataframe(stats_df, hide_index=True)

    except Exception as e:
        st.error(str(e))