# Подгоняет «векторно-чистый» материал (лента, вывеска) под мягкость сцен:
# лёгкое размытие, чернила сдвинуты в синеву как в сценах, мелкое зерно печати.
# usage: soften.py in.webp out.png sigma
import sys
import numpy as np
from PIL import Image, ImageFilter
src, out, sigma = sys.argv[1], sys.argv[2], float(sys.argv[3])
im = Image.open(src).convert('RGBA')
alpha = im.split()[3].filter(ImageFilter.GaussianBlur(sigma * 0.7))
rgb = np.asarray(im.convert('RGB').filter(ImageFilter.GaussianBlur(sigma))).astype(np.float32)
L = rgb.mean(2)
ink = np.clip((170 - L) / 140, 0, 1)[..., None]                    # насколько пиксель — чернила
rgb = rgb + ink * (np.array([8, 27, 60], np.float32) - np.array([10, 24, 43], np.float32)) * 1.6
rng = np.random.default_rng(7)
grain = np.asarray(Image.fromarray((rng.normal(128, 40, L.shape)).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))).astype(np.float32)
rgb = rgb * (1 + (grain[..., None] - 128) / 128 * 0.035)
o = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert('RGBA'); o.putalpha(alpha); o.save(out)
