import re
import time
import os
import geoip2.database
import sqlite3
import ipaddress

from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver as Observer

# --- PATHS (Config .env) ---
LOG_FILE = os.getenv("LOG_FILE", "/var/log/auth.log")
DB_PATH = os.getenv("DB_PATH", "data/GeoLite2-City.mmdb")
SQLITE_FILE = os.getenv("SQLITE_FILE", "data/clean_data_sqlite.db")

# --- REGEX UNIVERSAL (ISO & Syslog + IPv4/v6) ---
LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\S+).*?sshd(?:-session)?.*?\b(?P<ip>(?:(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4})|(?:\d{1,3}\.){3}\d{1,3})\b"
)

if os.path.exists(LOG_FILE):
    last_position = os.path.getsize(LOG_FILE)
else:
    last_position = 0

def parse_logs():
    global last_position
    print(f"Reading {LOG_FILE} from position {last_position}...")

    try:

        with geoip2.database.Reader(DB_PATH) as reader, open(LOG_FILE, "r") as f_in:
            f_in.seek(last_position)
            
            con = sqlite3.connect(SQLITE_FILE)
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS connections(timestamp TEXT, ip TEXT, country TEXT, city TEXT, lat REAL, lon REAL)")

            for line in f_in:
                line = line.strip()
                if not line: continue
                
                match = LOG_PATTERN.search(line)
                if match:
                    ip_raw = match.group("ip")
                    timestamp = match.group("timestamp")
                    
                    try:
                        # IP validation
                        ip_obj = ipaddress.ip_address(ip_raw)
                        ip_str = str(ip_obj)

                        if ip_obj.is_private or ip_obj.is_link_local:
                            # Fallback Local
                            country, city = "Local LAN", "Local"
                            lat, lon = 37.3912, -4.7712 
                        else:
                            response = reader.city(ip_str)
                            country = response.country.name or "Unknown"
                            city = response.city.name or "Unknown"
                            lat = response.location.latitude
                            lon = response.location.longitude

                        sqlite_save(con, cur, timestamp, ip_str, country, city, lat, lon)
                        print(f"[OK] Detected: {ip_str} ({city})")

                    except (ValueError, geoip2.errors.AddressNotFoundError):
                        continue
                    except Exception as e:
                        print(f"[ERROR] IP processing failed {ip_raw}: {e}")
            
            last_position = f_in.tell()
            con.close()
            
    except FileNotFoundError:
        print(f"Error! can't find the file. {LOG_FILE}")
    except Exception as e:
        print(f"Unexpected error in parse_logs: {e}")

    print(f"--- PROCESS COMPLETED ---\n")

def sqlite_save(con, cur, timestamp, ip, country, city, lat, lon):
    query = "INSERT INTO connections (timestamp, ip, country, city, lat, lon) VALUES (?, ?, ?, ?, ?, ?)"
    try: 
        cur.execute(query, (timestamp, ip, country, city, lat, lon))
        con.commit()
    except sqlite3.Error as e:
        print(f"Error inserting into SQLite: {e}")

class LogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        
        change = os.path.abspath(event.src_path)
        obj = os.path.abspath(LOG_FILE)

        if change == obj or os.path.dirname(change) == obj:
           
            time.sleep(0.2) 
            print(f"[*] Change detected in {os.path.basename(LOG_FILE)}")
            parse_logs()

if __name__ == "__main__":
    
    parse_logs()

    log_handler = LogHandler()
    observer = Observer() 
    
    log_dir = os.path.dirname(os.path.abspath(LOG_FILE))
    observer.schedule(log_handler, path=log_dir, recursive=False)
    observer.start()

    print(f"-- Observer active {log_dir} (POLLING MODE) --")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
