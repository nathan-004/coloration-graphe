from PIL import Image, ImageDraw, ImageFont
import hashlib
import json
from collections import defaultdict

from utils import bar_animation

font = ImageFont.load_default()

from collections import deque
from typing import NamedTuple

class Bbox(NamedTuple):
    minx: int
    miny: int
    maxx: int
    maxy: int

class Region(dict):
    def __init__(self, pixels: list):
        """
        Parameters
        ----------
        pixels: list[tuple[int, int]]
        """

        super().__init__({
            "pixels": pixels,
            "bbox": self._get_bbox(pixels)
        })

    def _get_bbox(self, pixels: list) -> Bbox:
        """
        Parameters
        ----------
        pixels: list[tuple[int, int]]
        """

        minx, maxx = min(pixels, key = lambda x : x[0])[0], max(pixels, key = lambda x : x[0])[0]
        miny, maxy = min(pixels, key = lambda x : x[1])[1], max(pixels, key = lambda x : x[1])[1]

        return Bbox(minx, miny, maxx, maxy)

    @property
    def pixels(self) -> list:
        """
        Returns
        -------
        Liste de positions
            list[tuple[int, int]]
        """
        return self["pixels"]

    @property
    def bbox(self) -> Bbox:
        return self["bbox"]

    @property
    def center(self):
        x, y = sum([point[0] for point in self.pixels]), sum([point[1] for point in self.pixels])
        return int(x/len(self.pixels)), int(y/len(self.pixels))

def distance(p1: tuple, p2: tuple) -> float:
    dr = p1[0] - p2[0]
    dg = p1[1] - p2[1]
    db = p1[2] - p2[2]

    return (dr**2 + dg**2 + db**2)**0.5

def get_thresold(pixels: Image, w, h):
    diffs = []

    for y in range(h):
        for x in range(w):

            c = pixels[x, y]

            for dx, dy in [(1,0), (0,1)]:
                nx, ny = x+dx, y+dy

                if nx < w and ny < h:
                    c2 = pixels[nx, ny]
                    d = distance(c, c2)
                    if 1 < d < 400:
                        diffs.append(d)

    diffs.sort()
    print(diffs[int(len(diffs) * 0.9)], sum(diffs)/len(diffs))
    return sum(diffs)/len(diffs)

def get_outlines(img_path: str, seuil_distance: float = None, display: bool = True) -> Image:
    """Renvoie une image noir et blanc (noir pour contour)"""
    img = Image.open(img_path).convert("RGBA")
    pixels = img.load()

    if seuil_distance is None:
        seuil_distance = get_thresold(pixels, *img.size)
    result = Image.new("RGB", (img.width, img.height), (255, 255, 255))

    for y in bar_animation(range(img.height), title="Détection contours"):
        for x in range(img.width):
            pixel = pixels[x, y]

            if pixel[3] == 0:
                result.putpixel((x, y), (0, 0, 0))

            neighbours = []

            for var_x in range(-1, 2):
                for var_y in range(-1, 2):

                    nx, ny = x + var_x, y + var_y

                    if 0 <= nx < img.width and 0 <= ny < img.height:
                        neighbour = pixels[nx, ny]

                        if neighbour[3] == 255:
                            neighbours.append(neighbour)

            if any([distance(pixel, n) >= seuil_distance for n in neighbours]):
                result.putpixel((x, y), (0, 0, 0))
            #print([distance(pixel, n) for n in neighbours])

    if display:
        result.show()

    return result

def get_regions_pixels(img: Image, min_pixels_region: int = 150, allow_cut_regions: bool = False, display: bool = True) -> Image:
    pixels = img.load()
    visited = set()
    regions = []
    res = Image.new("RGB", (img.width, img.height))

    n = 0

    for y in bar_animation(range(img.height), title="Obtention des régions"):
        for x in range(img.width):
            if (x, y) in visited:
                continue

            if pixels[x, y] != (255, 255, 255):
                continue

            stack = deque([(x, y)])
            region_pixels = []

            cut_region = False

            while stack:
                cur_x, cur_y = stack.pop()

                if (cur_x, cur_y) in visited:
                    continue

                if pixels[cur_x, cur_y] != (255, 255, 255):
                    continue

                region_pixels.append((cur_x, cur_y))
                visited.add((cur_x, cur_y))

                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = cur_x + dx, cur_y + dy

                    if 0 <= nx < img.width and 0 <= ny < img.height:
                        stack.append((nx, ny))
                    else:
                        cut_region = True

            if cut_region and not allow_cut_regions:
                if len(region_pixels) > min_pixels_region:
                    for x, y in region_pixels:
                        res.putpixel((x, y), (133, 133, 255))
                continue

            if len(region_pixels) > min_pixels_region:
                r = Region(region_pixels)
                area = len(region_pixels)
                width = r.bbox.maxx - r.bbox.minx
                height = r.bbox.maxy - r.bbox.miny

                if min(width, height) < 3 or area / (width * height) < 0.2:
                    continue

                regions.append(region_pixels)
                for x, y in region_pixels:
                    res.putpixel((x, y), (255, 255, 255))

    if display:
        res.show()
    return regions, res

def display_regions(regions: list, width: int = None, height: int = None) -> Image:
    if width is None or height is None:
        max_x = max([region.bbox.maxx for region in regions]) + 1 if regions else 0
        max_y = max([region.bbox.maxy for region in regions]) + 1 if regions else 0
        if width is None:
            width = max_x
        if height is None:
            height = max_y

    result = Image.new("RGB", (width, height), (0, 0, 0))

    for region in regions:
        for x, y in region.pixels:
            result.putpixel((x, y), (255, 255, 255))

    pixels = result.load()
    for region in regions:
        bbox = region.bbox

        for x in range(bbox.minx, bbox.maxx + 1):
            pixels[x, bbox.miny] = (255, 0, 0)

        for x in range(bbox.minx, bbox.maxx + 1):
            pixels[x, bbox.maxy] = (255, 0, 0)

        for y in range(bbox.miny, bbox.maxy + 1):
            pixels[bbox.minx, y] = (255, 0, 0)

        for y in range(bbox.miny, bbox.maxy + 1):
            pixels[bbox.maxx, y] = (255, 0, 0)

    # Ajouter les indices des régions
    draw = ImageDraw.Draw(result)
    for idx, region in enumerate(regions):
        bbox = region.bbox

        center_x = (bbox.minx + bbox.maxx) // 2
        center_y = (bbox.miny + bbox.maxy) // 2

        draw.text((center_x, center_y), str(idx), fill=(0, 0, 0), font=font)

    result.show()

    return result

def collide_bbox(r1: Region, r2: Region) -> bool:
    return not (
        r1.bbox.maxx < r2.bbox.minx or
        r1.bbox.minx > r2.bbox.maxx or
        r1.bbox.maxy < r2.bbox.miny or
        r2.bbox.miny > r2.bbox.maxy
    )

def dilate_region(region_pixels: Region, pixels, img_size, iterations = 1):
    w, h = img_size
    current = set(region_pixels)

    for _ in range(iterations):
        new_pixels = set(current)

        for x, y in current:
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:  # 4-connexité
                nx, ny = x + dx, y + dy

                if 0 <= nx < w and 0 <= ny < h:
                    if pixels[nx, ny] == (255, 255, 255) or pixels[nx, ny] == (0, 0, 0):
                        new_pixels.add((nx, ny))

        current = new_pixels

    return current

def get_graph(regions: list, img: Image) -> dict:
    dic = {}
    dilated_regions = []
    pixels = img.load()

    for idx, cur_r in bar_animation(regions, title="Création du graphe", refresh= 1, get_idx=True):
        dilated_regions.append(dilate_region(cur_r.pixels, pixels, img.size, 10))

    for idx, cur_r in enumerate(regions):
        neighbours = []
        for idx2, r2 in enumerate(regions):
            if idx == idx2:
                continue
            
            if collide_bbox(cur_r, r2):
                print("Collide bbox")
                print(dilated_regions[idx] & dilated_regions[idx2])
                if dilated_regions[idx] & dilated_regions[idx2]:
                    print("Collide regions touche")
                    neighbours.append(idx2)
        dic[idx] = neighbours

    return dic

def image_sha1(path: str) -> int:
    img = Image.open(path).convert("RGB").resize((512, 512))
    return hashlib.sha1(img.tobytes()).hexdigest()

def save_map(graph: dict, img: Image, regions: list, original_img_path: str):
    img_signature = image_sha1(original_img_path)
    centers = [region.center for region in regions]

    img_path = f"saves/imgs/{img_signature}.jpg"
    img.save(img_path)

    formated = {
        "graph": graph,
        "img_path": img_path,
        "centers": centers
    }

    with open(f"saves/{img_signature}.json", "w") as f:
        json.dump(formated, f)

def load_map(img_path: str = "", img_signature: str = None) -> dict:
    if img_signature is None:
        img_signature = image_sha1(img_path)

    try:
        with open(f"saves/{img_signature}.json") as f:
            res = json.load(f)
            res["graph"] = {int(key): value for key, value in res["graph"].items()}
            return res
    except FileNotFoundError:
        return None

if __name__ == "__main__":
    img = get_outlines("assets/imgs/regions_angleterre.png", display=True)
    regions_pixels, img_regions = get_regions_pixels(img, display=True)
    regions = [Region(r) for r in regions_pixels]

    display_regions(regions)
    print(get_graph(regions, img))