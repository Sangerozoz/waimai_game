# County Region isolated viewer

Cocos Creator 3.8.8. Only native whole-region art; no gameplay or save connection.

- `assets/scripts/AtlasModel.ts`: atlas types, fixed projection and route eligibility.
- `assets/scripts/RegionStream.ts`: bounded asynchronous native image streaming and release.
- `assets/scripts/CountyRegion.ts`: scene, camera controls and independent rider API.
- `runtime-data/region-atlas.json`: current PM-derived image records; A is preview-only.
- `tools/prepare-runtime.py <package-dir>`: native SHA-checked package import.
- `../scripts/build-county-region.sh --deploy`: necessary build and isolated deployment.

Report and stable data contract: `../../docs/reviews/county-region-20261103/`.
New source has not been tested or rendered. Build Finished evidence is not runtime acceptance.
