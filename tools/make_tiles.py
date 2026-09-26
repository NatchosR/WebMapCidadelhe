"""Cut the drone orthophotos (GeoTIFF, EPSG:32629 / UTM 29N) into light WebP web-map tiles
(tiles/{z}/{x}/{y}.webp, standard XYZ / Web-Mercator scheme) for the Leaflet page.

Usage:  python make_tiles.py <folder with *_orthophoto.tif> <output tiles folder>
Needs:  numpy, tifffile, Pillow
"""
import sys, os, math, glob
import numpy as np, tifffile
from PIL import Image

SRC, OUT = sys.argv[1], sys.argv[2]
ZMAX, ZMIN, QUALITY, TS = 21, 14, 72, 256   # z21 ~ 5.6 cm/pixel here, matching the 5 cm drone images

# ---------- WGS84 -> UTM zone 29N (Krüger series) ----------
a, f = 6378137.0, 1 / 298.257223563
n = f / (2 - f)
A = a / (1 + n) * (1 + n**2 / 4 + n**4 / 64)
alpha = [n/2 - 2*n**2/3 + 5*n**3/16, 13*n**2/48 - 3*n**3/5, 61*n**3/240]
k0, E0, lon0 = 0.9996, 500000.0, math.radians(29 * 6 - 183)
c2 = 2 * math.sqrt(n) / (1 + n)

def ll_to_utm(lat, lon):                      # numpy arrays, degrees
    phi, lam = np.radians(lat), np.radians(lon) - lon0
    t = np.sinh(np.arctanh(np.sin(phi)) - c2 * np.arctanh(c2 * np.sin(phi)))
    xi = np.arctan2(t, np.cos(lam))
    eta = np.arctanh(np.sin(lam) / np.sqrt(1 + t * t))
    E = eta.copy(); N = xi.copy()
    for j in range(1, 4):
        E += alpha[j-1] * np.cos(2*j*xi) * np.sinh(2*j*eta)
        N += alpha[j-1] * np.sin(2*j*xi) * np.cosh(2*j*eta)
    return E0 + k0 * A * E, k0 * A * N

# ---------- Web-Mercator tile maths ----------
def tile_pixel_lonlat(z, tx, ty):
    """lon/lat of the centre of every pixel of tile (z, tx, ty)."""
    size = TS * 2**z
    px = (tx * TS + np.arange(TS) + 0.5) / size
    py = (ty * TS + np.arange(TS) + 0.5) / size
    lon = px * 360 - 180
    lat = np.degrees(np.arctan(np.sinh(math.pi * (1 - 2 * py))))
    return np.meshgrid(lon, lat)

def lonlat_to_tile(lon, lat, z):
    s = 2**z
    x = (lon + 180) / 360 * s
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * s
    return int(x), int(y)

# ---------- read orthophotos ----------
ortho = []
for path in sorted(glob.glob(os.path.join(SRC, "*_orthophoto.tif"))):
    with tifffile.TiffFile(path) as tf:
        g = tf.geotiff_metadata
        assert g["ProjectedCSTypeGeoKey"] == 32629, "expected EPSG:32629"
        img = tf.asarray()
    if img.shape[2] == 3:
        img = np.dstack([img, np.full(img.shape[:2], 255, np.uint8)])
    sx, sy = g["ModelPixelScale"][:2]
    x0, y0 = g["ModelTiepoint"][3:5]
    h, w = img.shape[:2]
    ortho.append(dict(name=os.path.basename(path), img=img, x0=x0, y0=y0, sx=sx, sy=sy, w=w, h=h))
    print("read", path, img.shape)

def sample(o, E, N):
    """bilinear RGBA sample of orthophoto o at UTM coords (E, N)."""
    c = (E - o["x0"]) / o["sx"] - 0.5
    r = (o["y0"] - N) / o["sy"] - 0.5
    inside = (c >= 0) & (r >= 0) & (c < o["w"] - 1) & (r < o["h"] - 1)
    out = np.zeros(E.shape + (4,), np.float32)
    if not inside.any():
        return out
    ci, ri = np.floor(c[inside]).astype(int), np.floor(r[inside]).astype(int)
    fc, fr = (c[inside] - ci)[:, None], (r[inside] - ri)[:, None]
    im = o["img"]
    v = (im[ri, ci] * (1 - fc) * (1 - fr) + im[ri, ci + 1] * fc * (1 - fr)
         + im[ri + 1, ci] * (1 - fc) * fr + im[ri + 1, ci + 1] * fc * fr)
    out[inside] = v
    return out

# tile range at ZMAX covering all orthophotos (corners -> lat/lon via a coarse inverse search)
def utm_bbox_to_tiles(o, z):
    # corners of the orthophoto in UTM -> lon/lat by Newton on ll_to_utm (few iterations)
    xs = [o["x0"], o["x0"] + o["w"] * o["sx"]]
    ys = [o["y0"], o["y0"] - o["h"] * o["sy"]]
    tiles = []
    for X in xs:
        for Y in ys:
            lat, lon = 40.9, -7.12
            for _ in range(20):
                e, nn = ll_to_utm(np.array(lat), np.array(lon))
                lat += (Y - nn) / 111000.0
                lon += (X - e) / (111000.0 * math.cos(math.radians(lat)))
            tiles.append(lonlat_to_tile(lon, lat, z))
    return (min(t[0] for t in tiles), max(t[0] for t in tiles), min(t[1] for t in tiles), max(t[1] for t in tiles))

def save(tile_rgba, z, x, y):
    if tile_rgba[..., 3].max() == 0:
        return False
    d = os.path.join(OUT, str(z), str(x))
    os.makedirs(d, exist_ok=True)
    Image.fromarray(tile_rgba, "RGBA").save(os.path.join(d, f"{y}.webp"), "WEBP", quality=QUALITY, method=6)
    return True

# ---------- max zoom: resample from the orthophotos ----------
level = {}
todo = set()
for o in ortho:
    x0, x1, y0, y1 = utm_bbox_to_tiles(o, ZMAX)
    todo |= {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
for (x, y) in sorted(todo):
    lon, lat = tile_pixel_lonlat(ZMAX, x, y)
    E, N = ll_to_utm(lat, lon)
    acc = np.zeros((TS, TS, 4), np.float32)
    for o in ortho:                           # later orthophotos drawn on top where they have data
        s = sample(o, E, N)
        al = s[..., 3:4] / 255.0
        acc[..., :3] = acc[..., :3] * (1 - al) + s[..., :3] * al
        acc[..., 3:4] = np.maximum(acc[..., 3:4], s[..., 3:4])
    t = np.clip(acc + 0.5, 0, 255).astype(np.uint8)
    if t[..., 3].max() > 0:
        level[(x, y)] = t
        save(t, ZMAX, x, y)
print("z", ZMAX, len(level), "tiles")

# ---------- lower zooms: 2x2 children -> 1 parent ----------
for z in range(ZMAX - 1, ZMIN - 1, -1):
    parents = {}
    for (x, y), t in level.items():
        parents.setdefault((x // 2, y // 2), {})[(x % 2, y % 2)] = t
    level = {}
    for (px, py), kids in parents.items():
        big = np.zeros((TS * 2, TS * 2, 4), np.uint8)
        for (dx, dy), t in kids.items():
            big[dy * TS:(dy + 1) * TS, dx * TS:(dx + 1) * TS] = t
        # premultiplied-alpha downsample so transparent edges don't turn dark
        im = Image.fromarray(big, "RGBA").convert("RGBa").resize((TS, TS), Image.LANCZOS).convert("RGBA")
        t = np.asarray(im)
        level[(px, py)] = t
        save(t, z, px, py)
    print("z", z, len(level), "tiles")
