# Map sample source and licence

This sample contains an OpenStreetMap extract of central Matsumoto, Japan, downloaded on 2026-10-27, plus a larger city road extract and scenery downloaded on 2026-10-28. Bounds, queries and individual SHA-256 values are recorded in source.json, city-roads-query.txt and details/manifest.json. The in-game place labels are fictional. Geometry is real OSM data; speed, roughness, prices and delivery timing are game parameters, not real-world observations.

© OpenStreetMap contributors. The source.osm and derived city.json data are made available under the Open Database License (ODbL) 1.0: https://opendatacommons.org/licenses/odbl/1-0/. Attribution details: https://www.openstreetmap.org/copyright. This notice applies to the map data, separately from application code.

Reproduce the offline derived data from the project root:

```sh
python3 scripts/import-map-sample.py data/map-sample/source.osm assets/resources/map-sample/city.json data/map-sample/city-roads.osm
python3 scripts/import-map-details.py assets/resources/map-sample/city.json assets/resources/map-sample/city.json 'data/map-sample/details/*.osm'
```

The importer retains source node identity and one-way direction; it does not create connections from geometric line crossings. This is a local game graph, not a general navigation engine: source turn-restriction relations are not imported. Source roads unsuitable for the selected sample profile are excluded. No live map tile or navigation service is called at runtime.

The road network covers approximately 12 km across the city: 42,102 road nodes, 9,970 road pieces and 128 fictional places (27 merchants and 101 customer addresses). Places use the largest directed strongly connected component. New places prefer dense street junctions rather than isolated service-road ends. The eight previous sample places are retained where reachable; their identities are in legacy-pois.json.

The scenery supplement covers the complete query bounds (south 36.18, west 137.92, north 36.29, east 138.05) using a 4×4 grid. Region 12 is split into four quadrants: 19 complete XML source files in total. One small quadrant uses the public OSM map API; the others use the Overpass endpoints named in each source record. Failed, timed-out and incomplete responses are not included. Downloads are offline preparation only; the retained sources allow rebuilding without more network requests. The fetch helper defaults to serial requests and validates cached bounds and SHA values. Public endpoint information: https://wiki.openstreetmap.org/wiki/Overpass_API.

The final derived data contains 3,524 building polygons, 1,033 land/water polygons and 492 waterway paths. New geometry is clipped and deduplicated, with farmland, residential, commercial, green and water ground layers. The scenery step does not change road nodes, edges, POIs, labels or the save map identity. One pre-existing base waterway extends slightly beyond the query boundary and is preserved. Query coverage does not mean every real building is mapped: only selected OSM ways are imported; relation multipolygons and unmapped features are not synthesized.

Rendering keeps major roads visible in overview and loads 600 m road/building detail tiles near the camera, with a bounded cache. Routing uses uncompressed road travel seconds. DeliveryClock separately maps the displayed delivery duration to animation time at 360:1, capped at 12 seconds.

city-roads.osm is the complete XML response for the saved road-only query. Licence and source notices apply to all source extracts and the derived city.json database. Attribution remains visible in the game.
