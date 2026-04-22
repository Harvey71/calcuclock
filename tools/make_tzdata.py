import os
import pytz

START_YEAR = 2026
END_YEAR = 2036
OUTPUT_DIR = "../code/_zones"


def generate_all_zones():
    all_zones = pytz.all_timezones
    for zone_name in all_zones:
        parts = zone_name.split('/')
        if len(parts) < 2:
            continue
        rel_path = os.path.join(OUTPUT_DIR, *parts[:-1])
        file_name = f"{parts[-1]}.py"
        full_path = os.path.join(rel_path, file_name)
        os.makedirs(rel_path, exist_ok=True)
        try:
            tz = pytz.timezone(zone_name)
            if hasattr(tz, '_utc_transition_times'):
                transitions = []
                for i in range(len(tz._utc_transition_times)):
                    trans_time = tz._utc_transition_times[i]
                    if START_YEAR <= trans_time.year <= END_YEAR:
                        offset = int(tz._transition_info[i][0].total_seconds())
                        timestamp = int(trans_time.timestamp())
                        transitions.append((timestamp, offset))
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(f"tz_data = {transitions}\n")
        except Exception as e:
            print(f"Error at {zone_name}: {e}")


if __name__ == "__main__":
    generate_all_zones()