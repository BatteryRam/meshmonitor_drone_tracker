# Drone Warning script for MeshMonitor

A script that pulls live drone data from [the Mapa.ua drone strike tracker](https://mapa.ua) and sends a warning to the Meshtastic network if an active drone enters a specified area.
This script is designed to be run by [MeshMonitor](https://github.com/yeraze/meshmonitor).

### Dependencies:


- geopandas
- redis

geopandas also requires GDAL to be installed. For docker installations of MeshMonitor, use the add_libraries.Dockerfile to add the dependency to the container. 
Confirmed to be working with Python 3.12

### Configuration:

Default configuration file is config.json inside the MeshMonitor script directory (/data/scripts/ inside the MeshMonitor Docker container). To use a different configuration file, use `drones.py [insert path to configuration file here]` inside of MeshMonitor script arguments. 

Configuration options; 

- border_data_file - path to a GeoJson data file containing GPS coordinates of the target area to monitor. 
- warning_distance_km - Distance in kilometers around the target area that triggers a warning.
- warning_message - Warning message to send to the mesh when new objects enter the warning distance. Use {} inside the message to include the number of objects detected during the round.
- redis_host - Address of the redis database to cache which drones have already been detected. Default is "localhost"
- redis_port - Port of the redis database.. Default is 6379.
- cache_ttl - How long each drone ID is held in cache (in seconds). Default is 24 hours.

### Border_data_file examples

Border data file (like border.geojson) accepts a GeoJson geometry object in the EPSG:4326 format (a.k.a GPS coordinates).
May also be put inside of the MeshMonitor scripts directory. Use /data/scripts/border.geojson inside of the config file if that is the case. 

Example: Track an area around one point on the map.

```json
{
    "type": "Point",
    "coordinates": [
            22.678725065409481, 
            49.037361625938331
        ]
}
```

Example 2: Track an area around a border.

```json
{
    "type": "LineString",
    "coordinates": [
        [
            22.678725065409481,
            49.037361625938331
        ],
        [
            22.6968604286659,
            49.045980361504519
        ],
        [
            22.780283099285668,
            49.048654838250229
        ],
        [
            22.829701964474111,
            49.019525017465639
        ],
        ...
    ]
}

```

Read about [GeoJson](https://en.wikipedia.org/wiki/GeoJSON#Geometries) format here.









