import pandas as pd
import folium as fl
import sqlite3
import os

from folium.plugins import HeatMap
from apscheduler.schedulers.background import BlockingScheduler 

DB_PATH = os.getenv("SQLITE_FILE", "data/clean_data_sqlite.db")
OUTPUT_FILE = os.getenv("MAP_OUTPUT", "data/map.html")
MAP_INTERVAL = int(os.getenv("MAP_INTERVAL_SEC", 600))

def gen_map():
    if not os.path.exists(DB_PATH):
        print("Waiting DB...")
        return

    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT lat, lon from connections where timestamp > datetime('now', '-1 day')", con)
    con.close()

    if df.empty:
        print("No attacks to print.")
        return
    
    map = fl.Map(location=[20, 0], zoom_start=2, tiles="CartoDB dark_matter")

    HeatMap(
        df.values.tolist(), 
        radius=15, 
        blur=10, 
        min_opacity=0.4
    ).add_to(map)

    map.save(OUTPUT_FILE)
    print(f"[*] Map updated: {len(df)} new points")

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    gen_map()

    scheduler.add_job(gen_map, 'interval', seconds = MAP_INTERVAL)
    print(f"--- Map Scheduler started ({MAP_INTERVAL} sec) ---")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass