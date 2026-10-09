# Кадры «текущей воды» для фонтана на карте двора: те же пиксели картинки, сдвинутые
# волной (струи — вниз, вода в чаше — кругами наружу). Камень и кот не трогаются.
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
src, outdir = sys.argv[1], sys.argv[2]
X0, Y0, X1, Y1 = 610, 570, 950, 770                     # область кадра в исходнике 1536×1024
img = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)[Y0:Y1, X0:X1]
H, W = img.shape[:2]
def mask(draw_fn):
    m = Image.new('L', (W, H), 0); draw_fn(ImageDraw.Draw(m)); return m
o = lambda x, y: (x - X0, y - Y0)
streams = mask(lambda d: [d.rectangle([*o(712, 622), *o(748, 712)], 255), d.rectangle([*o(802, 622), *o(838, 706)], 255),
                          d.rectangle([*o(752, 582), *o(764, 618)], 255), d.rectangle([*o(786, 582), *o(800, 618)], 255)])
# камень не трогать: шпиль, верхняя чаша, ножка фонтана, кот
bowl = [(342, 160), (360, 130), (497, 118), (640, 130), (655, 160), (640, 195), (590, 240), (560, 260), (440, 260), (405, 240), (355, 195)]
keep = mask(lambda d: [d.rectangle([*o(765, 574), *o(787, 630)], 255), d.polygon([o(610 + x / 3, 570 + y / 3) for x, y in bowl], 255),
                       d.rectangle([*o(748, 640), *o(806, 724)], 255), d.polygon([o(830, 684), o(902, 684), o(902, 765), o(830, 765)], 255)])
k = np.asarray(keep.filter(ImageFilter.GaussianBlur(2))).astype(np.float32) / 255
ms = np.asarray(streams.filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255 * (1 - k)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
# вода в чаше: эллипс водной глади (центр 788,705, полуоси 136×29 — чуть внутри бортика);
# к краю движение плавно затухает до нуля, поэтому каменный бортик не плывёт
e = ((xx - (788 - X0)) / 136) ** 2 + ((yy - (705 - Y0)) / 29) ** 2
mb = np.clip((1 - e) / 0.35, 0, 1) * (1 - k)
cx, cy = 780 - X0, 708 - Y0
r = np.sqrt(((xx - cx) / 3.6) ** 2 + (yy - cy) ** 2)    # эллипс чаши ≈ 3.6 : 1
ux, uy = (xx - cx) / 3.6 / (r + 1e-3), (yy - cy) / (r + 1e-3)
def sample(dx, dy):
    x = np.clip(xx + dx, 0, W - 1.001); y = np.clip(yy + dy, 0, H - 1.001)
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int); fx, fy = (x - x0)[..., None], (y - y0)[..., None]
    a, b, c, d = img[y0, x0], img[y0, x0 + 1], img[y0 + 1, x0], img[y0 + 1, x0 + 1]
    return a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy
N = 6
alpha = np.clip(np.asarray(Image.fromarray(((np.maximum(ms, mb) > 0.02) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(3))).astype(np.float32), 0, 255)
for i in range(N):
    ph = 2 * np.pi * i / N
    ws = np.sin(2 * np.pi * yy / 11 - ph)               # струи: рисунок бежит вниз
    wb = np.sin(2 * np.pi * r / 13 - ph)                 # чаша: круги расходятся
    dx = ms * 1.1 * ws + mb * 1.2 * wb * ux * 3.6
    dy = ms * 1.1 * np.sin(2 * np.pi * yy / 17 - ph) + mb * 1.0 * wb * uy
    f = sample(dx, dy)
    Image.fromarray(np.dstack([np.clip(f, 0, 255), alpha]).astype(np.uint8), 'RGBA').save(f'{outdir}/f{i}.png')
print('frames', N, 'size', W, H, 'pos', X0, Y0)
