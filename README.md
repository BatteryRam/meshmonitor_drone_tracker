# Drone Warning script for MeshMonitor

A script that pulls live drone data from [the Mapa.ua drone strike tracker](https://mapa.ua) and sends a warning to the Meshtastic network if an active drone enters a specified area.
This script is designed to be run by [MeshMonitor](https://github.com/yeraze/meshmonitor).

### Basic Installation

1. Download docker-compose.yml and MeshMonitor_with_deps.Dockerfile into the same directory.
2. Build the docker environment using docker compose
3. Copy drones.py, config.json and target.geojson to your MeshMonitor's scripts directory
4. Edit config.json and target.geojson according to your preferences. 

Now you can call your script from within MeshMonitor. 


### Dependencies:

- geopandas
- redis

geopandas also requires GDAL to be installed. For docker installations of MeshMonitor, use the MeshMonitor_with_deps.Dockerfile to add the dependency to the container. 
Confirmed to be working with Python 3.12



### Configuration:

Default configuration file is config.json inside the MeshMonitor scripts directory (/data/scripts/config.json inside the MeshMonitor Docker container). To use a different configuration file, add the path to script arguments within MeshMonitor. 

Configuration options: 

- target_area_data_file - path to a GeoJson data file containing GPS coordinates of the target area to monitor. 
- warning_distance_km - Distance in kilometers around the target area that triggers a warning.
- warning_message - Warning message to send to the mesh when new objects enter the warning distance. Use {} inside the message to include the number of objects detected.
- redis_host - Address of the redis database to cache which drones have already been detected. Default is "localhost"
- redis_port - Port of the redis database. Default is 6379.
- cache_ttl - How long each drone ID is held in cache (in seconds). Default is 24 hours.

### target_area_data_file examples

Target data file (like target.geojson) accepts a GeoJson geometry object in the EPSG:4326 format (a.k.a GPS coordinates).
Put inside of the MeshMonitor scripts directory by default. 
Otherwise set target_area_data_file in config.json to your chosen path

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
        ]
    ]
}

```

Read about [GeoJson](https://en.wikipedia.org/wiki/GeoJSON#Geometries) format here.









