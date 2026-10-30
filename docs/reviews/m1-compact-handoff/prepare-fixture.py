from pathlib import Path
import shutil
root=Path.cwd();dest=root/'output/playwright/m1-compact-handoff/site'
if dest.exists():shutil.rmtree(dest)
shutil.copytree(root/'delivery-game/build/map-sample',dest)
shutil.copy2(root/'docs/reviews/m1-compact-handoff/fixture.js',dest/'fixture.js')
p=dest/'index.html';p.write_text(p.read_text().replace('<script>\n    System.import','<script src="fixture.js"></script>\n<script>\n    System.import'))
