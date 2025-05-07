# Import necessary libraries
from prefect import flow, task
from prefect_email import EmailServerCredentials, email_send_message
import pandas as pd
import time
import sqlite3, os
from nba_api.stats.endpoints import leaguedashplayerstats, leaguedashplayerbiostats

# Fetch player stats and bio for each season
@task(retries=3, retry_delay_seconds=60)
def fetch_season_data(season: str, per_mode="PerGame") -> pd.DataFrame:
    try:
        stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season, per_mode_detailed=per_mode)
        bio = leaguedashplayerbiostats.LeagueDashPlayerBioStats(season=season)
        df_stats = stats.get_data_frames()[0]
        df_bio = bio.get_data_frames()[0]
        df_combined = pd.merge(df_bio, df_stats, on="PLAYER_ID", suffixes=("_BIO", "_STATS"))
        df_combined["SEASON"] = season
        return df_combined
    except Exception as e:
        print(f"Failed for season {season}: {e}")
        return pd.DataFrame()

# Save the combined DataFrame to CSV and SQLite
@task
def save_to_csv(df: pd.DataFrame):
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/nba_combined_stats_bios_1996_2024.csv", index=False)

@task
def save_to_sqlite(df: pd.DataFrame):
    conn = sqlite3.connect("nba_player_data.db")
    df.to_sql("player_stats", conn, if_exists="replace", index=False)
    conn.close()

# Send email notification if the pipeline fails
@task
def send_failure_email():
    credentials = EmailServerCredentials.load("gmail-creds")
    email_send_message(
        email_to="your_email@example.com",
        subject="🚨 NBA ETL Pipeline Failed",
        msg="The NBA ETL pipeline failed to complete successfully.",
        email_server_credentials=credentials
    )
# Execute the ETL pipeline
@flow(name="NBA ETL Pipeline", retries=0)
def nba_etl_pipeline():
    try:
        all_data = []
        for year in range(1996, 2024):
            season = f"{year}-{str(year + 1)[-2:]}"
            print(f"Processing {season}")
            df = fetch_season_data(season)
            if not df.empty:
                all_data.append(df)
            time.sleep(1)  # Respect rate limits

        if not all_data:
            raise RuntimeError("No data collected — aborting pipeline.")

        combined = pd.concat(all_data, ignore_index=True)
        save_to_csv(combined)
        save_to_sqlite(combined)
        print("ETL complete.")
    except Exception as e:
        print(f"ETL failed: {e}")
        send_failure_email.submit()

if __name__ == "__main__":
    nba_etl_pipeline()