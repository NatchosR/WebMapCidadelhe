"""Convert the QGIS GeoPackages (EPSG:32629, UTM 29N) to compact web data (WGS84).
Pure standard library: sqlite3 + GPKG WKB parsing + Krüger-series inverse UTM."""
import sqlite3, struct, json, math, sys, os

SRC = sys.argv[1]   # folder containing all_tree_updated.gpkg and all_line.gpkg
OUT = sys.argv[2]   # e.g. the repo data/ folder

# ---------- inverse UTM (WGS84, Krüger series, ~mm accuracy) ----------
a, f = 6378137.0, 1 / 298.257223563
n = f / (2 - f)
A = a / (1 + n) * (1 + n**2 / 4 + n**4 / 64)
beta = [n/2 - 2*n**2/3 + 37*n**3/96, n**2/48 + n**3/15, 17*n**3/480]
delta = [2*n - 2*n**2/3 - 2*n**3, 7*n**2/3 - 8*n**3/5, 56*n**3/15]
k0, E0, zone = 0.9996, 500000.0, 29
lon0 = math.radians(zone * 6 - 183)

def utm_to_ll(E, N):
    xi = N / (k0 * A)
    eta = (E - E0) / (k0 * A)
    xi_p, eta_p = xi, eta
    for j in range(1, 4):
        xi_p -= beta[j-1] * math.sin(2*j*xi) * math.cosh(2*j*eta)
        eta_p -= beta[j-1] * math.cos(2*j*xi) * math.sinh(2*j*eta)
    chi = math.asin(math.sin(xi_p) / math.cosh(eta_p))
    phi = chi + sum(delta[j-1] * math.sin(2*j*chi) for j in range(1, 4))
    lam = lon0 + math.atan2(math.sinh(eta_p), math.cos(xi_p))
    return round(math.degrees(phi), 7), round(math.degrees(lam), 7)

# ---------- GPKG geometry blob -> WKB -> coords ----------
def gpkg_wkb(blob):
    flags = blob[3]
    env = (flags >> 1) & 7
    envlen = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[env]
    return blob[8 + envlen:]

def parse_wkb(b, o=0):
    bo = '<' if b[o] == 1 else '>'
    t = struct.unpack_from(bo + 'I', b, o + 1)[0]
    o += 5
    base = t % 1000
    dim = 3 if (t // 1000) in (1, 2) else (4 if t // 1000 == 3 else 2)
    if base == 1:
        c = struct.unpack_from(bo + 'd' * dim, b, o); return ('Point', c[:2]), o + 8 * dim
    if base == 2:
        k = struct.unpack_from(bo + 'I', b, o)[0]; o += 4; pts = []
        for _ in range(k):
            c = struct.unpack_from(bo + 'd' * dim, b, o); pts.append(c[:2]); o += 8 * dim
        return ('LineString', pts), o
    if base == 4:
        k = struct.unpack_from(bo + 'I', b, o)[0]; o += 4; pts = []
        for _ in range(k):
            g, o = parse_wkb(b, o); pts.append(g[1])
        return ('MultiPoint', pts), o
    if base == 5:
        k = struct.unpack_from(bo + 'I', b, o)[0]; o += 4; parts = []
        for _ in range(k):
            g, o = parse_wkb(b, o); parts.append(g[1])
        return ('MultiLineString', parts), o
    raise ValueError(f"unsupported WKB type {t}")

os.makedirs(OUT, exist_ok=True)

# ---------- row segments (UTM) for the tree -> row spacing lookup ----------
segs = []   # (ax, ay, bx, by, tree_spacing)
for g, sp in sqlite3.connect(f"{SRC}/all_line.gpkg").execute("select geom, tree_spacing from all_line"):
    (_, parts), _ = parse_wkb(gpkg_wkb(g))
    if isinstance(parts[0][0], float): parts = [parts]
    for p in parts:
        for (ax, ay), (bx, by) in zip(p[:-1], p[1:]):
            segs.append((ax, ay, bx, by, sp))

def row_spacing(x, y):
    """tree_spacing of the row line closest to the tree (trees lie on their line)."""
    best, sp = float("inf"), None
    for ax, ay, bx, by, s in segs:
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy
        t = 0 if l2 == 0 else max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / l2))
        d = (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2
        if d < best: best, sp = d, s
    return sp

# ---------- trees ----------
con = sqlite3.connect(f"{SRC}/all_tree_updated.gpkg")
rows = con.execute("select geom, species, category, land, instance, distance_m, planting_month "
                   "from all_tree_updated order by land, cast(instance as int), distance_m").fetchall()
species = sorted({r[1] for r in rows})
cats = sorted({r[2] for r in rows})
months = sorted({r[6] for r in rows})
lands = ["alagoa", "carrascal", "lagar"]
trees = []
for g, sp, cat, land, inst, dist, month in rows:
    (_, (x, y)), _ = parse_wkb(gpkg_wkb(g))
    lat, lng = utm_to_ll(x, y)
    trees.append([lat, lng, species.index(sp), cats.index(cat), lands.index(land),
                  int(inst), dist, months.index(month), row_spacing(x, y)])
with open(f"{OUT}/trees.js", "w", encoding="utf-8") as fh:
    fh.write("window.TREES = ")
    json.dump({"fields": ["lat", "lng", "species", "category", "land", "row", "distance_m", "month", "spacing_m"],
               "species": species, "categories": cats, "lands": lands, "months": months,
               "trees": trees}, fh, separators=(",", ":"), ensure_ascii=False)
    fh.write(";\n")

# ---------- row lines ----------
con = sqlite3.connect(f"{SRC}/all_line.gpkg")
feats = []
for g, ref, inst, spacing, cat, length in con.execute(
        "select geom, referenced_line, instance, tree_spacing, category, length from all_line"):
    (_, parts), _ = parse_wkb(gpkg_wkb(g))
    if isinstance(parts[0][0], float): parts = [parts]
    coords = [[list(reversed(utm_to_ll(x, y))) for x, y in p] for p in parts]
    coords = [[[round(c[0], 7), round(c[1], 7)] for c in p] for p in coords]
    feats.append({"type": "Feature",
                  "properties": {"ref": ref, "row": inst, "spacing": spacing, "category": cat,
                                 "length": round(length, 1) if length else None},
                  "geometry": {"type": "MultiLineString", "coordinates": coords}})
with open(f"{OUT}/rows.js", "w", encoding="utf-8") as fh:
    fh.write("window.ROWS = ")
    json.dump({"type": "FeatureCollection", "features": feats}, fh, separators=(",", ":"))
    fh.write(";\n")

# ---------- existing trees (optional layer) ----------
existing = []
if os.path.exists(f"{SRC}/existing_trees.gpkg"):
    for (g,) in sqlite3.connect(f"{SRC}/existing_trees.gpkg").execute("select geom from existing_trees"):
        (kind, c), _ = parse_wkb(gpkg_wkb(g))
        for x, y in (c if kind == "MultiPoint" else [c]):
            existing.append(list(utm_to_ll(x, y)))
with open(f"{OUT}/existing.js", "w", encoding="utf-8") as fh:
    fh.write("window.EXISTING = ")
    json.dump(existing, fh, separators=(",", ":"))
    fh.write(";\n")

print(len(existing), "existing trees;", len(trees), "trees;", len(feats), "lines;", species)
