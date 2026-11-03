#!/usr/bin/env python3
"""Apply the final display-only street-facing camera after layout generation."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'sample-layout.json'
layout = json.loads(path.read_text())
layout['cameraFocus'] = {
    'placementIds': ['neighbor-west-south', 'neighbor-west-middle', 'neighbor-west-north'],
    'map': [-1591, 75],
    'screenOffset': [0, -70],
    'padding': 3,
    'notes': 'Frame the existing western street-facing cafe and adjacent buildings with original road in foreground; other bank continues as background. No placement, road or source change.'
}
path.write_text(json.dumps(layout, ensure_ascii=False, indent=2) + '\n')
