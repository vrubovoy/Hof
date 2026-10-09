# Кадры порыва ветра для листвы на карте двора: те же пиксели, крона качается от ствола
# (верх сильнее), листья мелко дрожат. Кадр «покоя» не нужен: в покое слой скрыт.
# Пиксели берутся бикубически (Catmull-Rom), чтобы штриховка не мылилась; кадры потом
# увеличиваются в 2× тем же способом, что и сама карта (см. asset-prompt.txt, «Обработка»).
# usage: leaves.py scene-courtyard-map.png <папка> → <папка>/<имя>-f0…f7.png и список областей
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
src, outdir = sys.argv[1], sys.argv[2]
full = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
# имя: рамка (x0, y0, x1, y1), контур кроны, низ кроны (у ствола качания нет), размах в px
REGIONS = {
    'olive': ((0, 620, 570, 890), [(0, 682), (60, 684), (110, 690), (140, 668), (190, 647), (240, 637), (300, 634), (360, 634),
                                   (410, 648), (450, 660), (490, 686), (530, 716), (552, 742), (532, 782), (480, 802), (420, 800),
                                   (410, 890), (0, 890)], 890, 2.4),
    'bush-l': ((540, 592, 700, 732), [(548, 650), (575, 606), (640, 598), (690, 640), (684, 700), (640, 726), (570, 722)], 726, 1.6),
    'bush-r': ((880, 598, 1062, 742), [(888, 660), (920, 610), (990, 604), (1052, 650), (1048, 710), (990, 738), (912, 728)], 738, 1.6),
    'tree': ((400, 226, 566, 430), [(412, 300), (440, 240), (500, 232), (556, 280), (552, 380), (500, 420), (430, 410)], 425, 1.8),
}
ENV = [0.2, 0.6, 1.0, 0.8, 0.45, 0.05, -0.2, -0.08]   # качнуло, вернулось, чуть назад; края ≈ 0 — без рывка


def cubic(img, x, y):
    H, W = img.shape[:2]
    xi, yi = np.floor(x).astype(int), np.floor(y).astype(int); tx, ty = x - xi, y - yi
    def w(t):
        return [(-t**3 + 2*t**2 - t) / 2, (3*t**3 - 5*t**2 + 2) / 2, (-3*t**3 + 4*t**2 + t) / 2, (t**3 - t**2) / 2]
    wx, wy = w(tx), w(ty); out = 0
    for j in range(4):
        row = 0
        for i in range(4):
            row = row + img[np.clip(yi + j - 1, 0, H - 1), np.clip(xi + i - 1, 0, W - 1)] * wx[i][..., None]
        out = out + row * wy[j][..., None]
    return out
for name, ((x0, y0, x1, y1), poly, base, amp) in REGIONS.items():
    img = full[y0:y1, x0:x1]; H, W = img.shape[:2]
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in poly], 255)
    mk = np.asarray(m.filter(ImageFilter.GaussianBlur(6))).astype(np.float32) / 255
    alpha = np.asarray(m.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(5))).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    top = min(y for _, y in poly) - y0
    h = np.clip((base - y0 - yy) / max(1, base - y0 - top), 0, 1) ** 0.8
    for i, e in enumerate(ENV):
        ph = 2 * np.pi * i / len(ENV)
        dx = mk * (amp * e * h * (1 + 0.35 * np.sin(2 * np.pi * xx / 70 + yy / 40)) + 0.6 * np.sin(2 * np.pi * (xx / 17 + yy / 23) - ph))
        dy = mk * 0.5 * np.sin(2 * np.pi * (xx / 21 - yy / 19) - ph)
        f = cubic(img, np.clip(xx - dx, 0, W - 1), np.clip(yy - dy, 0, H - 1))
        Image.fromarray(np.dstack([np.clip(f, 0, 255), alpha]).astype(np.uint8), 'RGBA').save(f'{outdir}/{name}-f{i}.png')
    print(name, x0, y0, W, H)
