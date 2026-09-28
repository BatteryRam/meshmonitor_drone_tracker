"""
Simple MeshMonitor Drone Warning System
Author: BatteryRam

This script pulls live data from mapa.ua drone tracker and sends a warning to the Meshtastic Mesh when drones are detected within a specified distance away from the selected target.

"""

from geopandas import read_file, GeoSeries, GeoDataFrame
from shapely import Point
import requests
import json
import redis
import sys
import os

def parse_multi_level_array(objects):
    ids = []
    statuses = []
    geometries = []

    for drone in objects:
        if drone["lon"] is None or drone["lat"] is None:
            continue
        ids.append(str(drone["id"]))
        statuses.append(drone["status"])
        geometries.append(Point(drone["lon"], drone["lat"]))
    
    if "more" in objects:
        level = parse_multi_level_array(objects["more"])
        ids.extend(level[0])
        statuses.extend(level[1])
        geometries.extend(level[2])
    return ids, statuses, geometries



def main():
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else: 
        config_path = "/data/scripts/config.json"
    try:
        config = json.load(open(config_path, "r"))
    except Exception as e:
        if config_path == "/data/scripts/config.json":
            raise OSError(f"Cannot open config.json within scripts folder. Are you sure you have created the file? Error log: {e}")
        else:
            raise OSError(f"Cannot open {config_path} config file. Currently in folder {os.getcwd()}. Error log: {e}")
    if config.get("warning_distance_km", None) is None:
        raise Exception("warning_distance_km option is missing from configuration. Please set the minimum warning distance in the configuration file.")
    if config.get("warning_message", None) is None:
          raise Exception("warning_message option is missing from configuration. Please set your preferred warning message in the configuration file.")
    if config.get("target_area_data_file", None) is None:
          raise Exception("target_area_data_file option is missing from configuration. Please add the path to the target location file in the configuration file.")
    response = requests.get("https://mapa.ua/api/v1/current").json()

    if response["attack"] is None:
        return
    try:
        area = read_file(config.get("target_area_data_file", "/data/scripts/target.geojson"))
    except Exception as e:
        raise Exception(f"There was an error reading or parsing the target location file. Please ensure the file is GeoJSON-compliant. Error log: {e}")
    
    r = redis.Redis(host=config.get("redis_host", "localhost"), port=config.get("redis_port", 6379), decode_responses=True)

    parsed_array = parse_multi_level_array(response["objects"])
    drones = {"id": parsed_array[0], "status": parsed_array[1], "geometry": parsed_array[2]}
    

    df = GeoDataFrame(drones, crs="EPSG:4326")

    processed_drone_ids = []
    cursor = 0
    while(True):
        current = r.scan(cursor=cursor)
        cursor = current[0]
        processed_drone_ids.extend(current[1])
        if cursor == 0:
            break
    
    utm_crs = df.estimate_utm_crs()
    drones_to_process = df.loc[~(df["id"].isin(processed_drone_ids)) & (df["status"] == "active")]
    drones_to_process = drones_to_process.to_crs(utm_crs)
    area = area.to_crs(utm_crs)
    distances = drones_to_process.geometry.distance(area.geometry.iloc[0])
    
    active_drones = drones_to_process[distances < int(config["warning_distance_km"]) * 1000]

    new_drones = len(active_drones)
    ttl = config.get("cache_ttl", 86400)
    for record in active_drones["id"]:
        r.set(str(record), 0, ex=ttl)
    
    if new_drones > 0:
        print(json.dumps({"response": config["warning_message"].format(new_drones)}))
    

main()