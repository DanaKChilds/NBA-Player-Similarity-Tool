# Import necessary libraries
import pandas as pd
import time
from nba_api.stats.endpoints import leaguedashplayerstats, leaguedashplayerbiostats
import os

# Define function to gather and merge NBA player stats and bios from 1996-97 season to 2023-24 season
def get_combined_stats_and_bios_1996_onward(per_mode="PerGame") -> pd.DataFrame:
    all_data = []
# Loop through each season
    for year in range(1996, 2024):
        season = f"{year}-{str(year + 1)[-2:]}"
        print(f"Fetching season: {season}")
        try:
# Fetch player statistics
            stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season, per_mode_detailed=per_mode)
            df_stats = stats.get_data_frames()[0]
            time.sleep(1)

# Fetch player bios
            bio = leaguedashplayerbiostats.LeagueDashPlayerBioStats(season=season)
            df_bio = bio.get_data_frames()[0]
            time.sleep(1)

# Merge two dataframes on PLAYER_ID
            df_combined = pd.merge(df_bio, df_stats, on="PLAYER_ID", suffixes=("_BIO", "_STATS"))
            df_combined["SEASON"] = season
            all_data.append(df_combined)

# Error handling
        except Exception as e:
            print(f"Failed on {season}: {e}")
            continue

    return pd.concat(all_data, ignore_index=True)

# Run ETL process if script is executed directly
if __name__ == "__main__":
    df = get_combined_stats_and_bios_1996_onward()

    os.makedirs("data", exist_ok=True)

# Save the combined data to a CSV file    
    df.to_csv("data/nba_combined_stats_bios_1996_2024.csv", index=False)
    print("✅ Data saved to data/nba_combined_stats_bios_1996_2024.csv")