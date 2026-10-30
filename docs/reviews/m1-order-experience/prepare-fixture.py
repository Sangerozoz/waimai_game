from pathlib import Path
import shutil
root=Path.cwd(); dest=root/'output/playwright/m1-order-experience/site'
# Rebuild only this task's isolated fixture output, never the user checkout or game state.
if dest.exists():shutil.rmtree(dest)
shutil.copytree(root/'delivery-game/build/map-sample',dest)
index=dest/'index.html';text=index.read_text();text=text.replace('<script>\n    System.import', '<script src="fixture.js"></script>\n<script>\n    System.import');index.write_text(text)
shutil.copy2(root/'docs/reviews/m1-order-experience/fixture.js',dest/'fixture.js')
