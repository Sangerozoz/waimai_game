"""Pure product-art layout preview. Does not import/run the game or any save.

No map input and no scene background. Vehicle pixels come from the unchanged
native master; only proportional downsampling/alpha compositing is performed.
The ownership line is deliberately non-numeric, not a user's inventory.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SCALE = 2  # Vector UI supersampling, not new native vehicle detail.
CARD = (684, 444)
VIEWPORT = (12, 8, 660, 268)
ART = (141, 8, 378, 252)
SOURCE = ROOT / "delivery-game/assets/resources/map-sample/anime/vehicles-20261031/V02-c-45.png"
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"


def font(size):
    return ImageFont.truetype(FONT, round(size * SCALE))


def rect(box):
    return tuple(round(v * SCALE) for v in box)


def text(draw, xy, value, size, fill="#061344", anchor="lm"):
    draw.text(tuple(round(v * SCALE) for v in xy), value, font=font(size), fill=fill, anchor=anchor)


def main():
    card = Image.new("RGBA", (CARD[0] * SCALE, CARD[1] * SCALE), "#EFFAFF")
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle(rect((0.5, 0.5, 683.5, 443.5)), radius=16, fill="#EFFAFF", outline="#79CEFF", width=3)
    x, y, w, h = VIEWPORT
    stage = Image.new("RGBA", (w * SCALE, h * SCALE))
    sd = ImageDraw.Draw(stage)
    # Neutral UI display surface, intentionally not a replacement city scene.
    for row in range(stage.height):
        t = row / max(1, stage.height - 1)
        rgb = tuple(round(a + (b - a) * t) for a, b in zip((247, 251, 253), (229, 237, 243)))
        sd.line((0, row, stage.width, row), fill=rgb + (255,))
    sx, sy, sw, sh = ART
    vehicle = Image.open(SOURCE).convert("RGBA")
    vehicle = vehicle.resize((sw * SCALE, sh * SCALE), Image.Resampling.LANCZOS)
    stage.alpha_composite(vehicle, (sx * SCALE, sy * SCALE))
    card.alpha_composite(stage, (x * SCALE, y * SCALE))
    # These labels explain a static template; no ownership count is invented.
    text(draw, (12, 303), "满载", 32)
    text(draw, (132, 303), "拥有数：运行时读取", 21)
    draw.rounded_rectangle(rect((491, 287, 617, 317)), radius=9, fill="#087FFF")
    text(draw, (554, 302), "新购 Lv.1", 18, "#FFFFFF", "mm")
    text(draw, (16, 351), "速度  ×1.2", 22)
    text(draw, (236, 351), "容量  7 kg", 22)
    text(draw, (16, 394), "收入加成 +50%", 22)
    draw.rounded_rectangle(rect((448, 349, 660, 411)), radius=10, fill="#FF8314", outline="#FFAC38", width=3)
    text(draw, (554, 380), "购买 1000金币", 23, "#FFFFFF", "mm")
    preview = card.convert("RGB").resize(CARD, Image.Resampling.LANCZOS)
    target = OUT / "model-03-product-layout-static.png"
    preview.save(target)
    stage_target = OUT / "model-03-product-preview-static.png"
    stage.convert("RGB").resize((w, h), Image.Resampling.LANCZOS).save(stage_target)
    records = []
    for path in (target, stage_target):
        with Image.open(path) as im:
            records.append({"path": str(path.relative_to(ROOT)), "size": list(im.size), "mode": im.mode,
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                            "kind": "static_product_layout_not_game_screenshot", "sceneBackground": None,
                            "userInventoryRepresented": False})
    print(json.dumps(records, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
