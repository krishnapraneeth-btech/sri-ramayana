import os
from PIL import Image, ImageDraw

RAW_DIR = "/home/user/ramayana_app/art_raw"
IMG_OUT = "/home/user/ramayana_app/android/assets/www/images"
RES_DIR = "/home/user/ramayana_app/android/res"

os.makedirs(IMG_OUT, exist_ok=True)

# 1. Convert emblem.png to Android mipmap launcher icons + web emblem
emblem_path = os.path.join(RAW_DIR, "emblem.png")
emblem = Image.open(emblem_path).convert("RGBA")

# Save web emblem
emblem_web = emblem.resize((512, 512), Image.Resampling.LANCZOS)
emblem_web.convert("RGB").save(os.path.join(IMG_OUT, "emblem.jpg"), "JPEG", quality=92, optimize=True)

# Rounded square mask for adaptive/legacy launcher icons
sizes = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}
for folder, sz in sizes.items():
    out_dir = os.path.join(RES_DIR, folder)
    os.makedirs(out_dir, exist_ok=True)
    icon = emblem.resize((sz, sz), Image.Resampling.LANCZOS)
    mask = Image.new("L", (sz, sz), 0)
    draw = ImageDraw.Draw(mask)
    radius = max(8, sz // 5)
    draw.rounded_rectangle([0, 0, sz - 1, sz - 1], radius=radius, fill=255)
    out = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    out.paste(icon, (0, 0), mask)
    out.save(os.path.join(out_dir, "ic_launcher.png"), "PNG", optimize=True)

# 2. Convert scene_01 .. scene_09 to crisp 1280x720 JPEGs
scenes = [
    "scene_01_yagna.png",
    "scene_02_birth.png",
    "scene_03_vishwamitra.png",
    "scene_04_swayamvar.png",
    "scene_05_exile.png",
    "scene_06_chitrakoot.png",
    "scene_07_golden_deer.png",
    "scene_08_jatayu.png",
    "scene_09_shabari_hanuman.png",
]

for fname in scenes:
    src = os.path.join(RAW_DIR, fname)
    im = Image.open(src).convert("RGB")
    im_resized = im.resize((1280, 720), Image.Resampling.LANCZOS)
    out_name = fname.replace(".png", ".jpg")
    im_resized.save(os.path.join(IMG_OUT, out_name), "JPEG", quality=88, optimize=True)
    print("Optimized:", out_name, os.path.getsize(os.path.join(IMG_OUT, out_name)))
