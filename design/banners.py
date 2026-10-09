# Кадры знамён на карте двора, которые тихо колышутся: те же пиксели, ткань под древком
# изгибается волной, бегущей вниз; древко неподвижно, к хвосту размах больше.
# usage: banners.py scene-courtyard-map.png <папка> → <папка>/<имя>-f0…f7.png
import sys
import numpy as np
from PIL import Image, ImageFilter
src, outdir = sys.argv[1], sys.argv[2]
full = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
# имя: x0, x1 ткани, y под древком, y хвоста, размах в px
BANNERS = {'banner-gate-l': (60, 112, 388, 508, 1.6), 'banner-gate-r': (318, 366, 388, 505, 1.6), 'banner-tower': (1452, 1520, 312, 500, 1.9)}
PAD = 10
N = 8
for name, (x0, x1, ytop, ytip, amp) in BANNERS.items():
    bx0, by0, bx1, by1 = x0 - PAD, ytop - 4, x1 + PAD, ytip + PAD
    img = full[by0:by1, bx0:bx1]; H, W = img.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # размах: 0 у древка, полный к хвосту, снова 0 у краёв клочка — фон у краёв не сдвигается
    k = np.clip((yy - 4) / (ytip - ytop), 0, 1) ** 1.2 * np.clip((H - 3 - yy) / (PAD - 3), 0, 1)
    k *= np.clip(np.minimum(xx - 2, W - 3 - xx) / (PAD - 4), 0, 1)
    m = np.zeros((H, W), np.uint8); m[4:H - 4, 4:W - 4] = 255
    alpha = np.asarray(Image.fromarray(m).filter(ImageFilter.GaussianBlur(3))).astype(np.float32)
    for i in range(N):
        ph = 2 * np.pi * i / N
        dx = amp * k * np.sin(2 * np.pi * yy / 70 - ph)
        x = np.clip(xx - dx, 0, W - 1.001)
        xi = np.floor(x).astype(int); fx = (x - xi)[..., None]
        f = img[yy.astype(int), xi] * (1 - fx) + img[yy.astype(int), np.minimum(xi + 1, W - 1)] * fx
        Image.fromarray(np.dstack([np.clip(f, 0, 255), alpha]).astype(np.uint8), 'RGBA').save(f'{outdir}/{name}-f{i}.png')
    print(name, bx0, by0, W, H)
