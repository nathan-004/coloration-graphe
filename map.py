from PIL import Image, ImageDraw, ImageFont
import hashlib
import json


from utils import bar_animation

font = ImageFont.load_default(32)

from collections import deque
from typing import NamedTuple

class Bbox(NamedTuple):
    minx: int
    miny: int
    maxx: int
    maxy: int

class Region(dict):
    def __init__(self, pixels: list[tuple[int, int]]):
        super().__init__({
            "pixels": pixels,
            "bbox": self._get_bbox(pixels)
        })
    
    def _get_bbox(self, pixels: list[tuple[int, int]]) -> Bbox:
        minx, maxx = min(pixels, key = lambda x : x[0])[0], max(pixels, key = lambda x : x[0])[0]
        miny, maxy = min(pixels, key = lambda x : x[1])[1], max(pixels, key = lambda x : x[1])[1]

        return Bbox(minx, miny, maxx, maxy)
    
    @property
    def pixels(self) -> list[tuple[int, int]]:
        return self["pixels"]
    
    @property
    def bbox(self) -> Bbox:
        return self["bbox"]
    
    @property
    def center(self):
        minx, miny, maxx, maxy = self.bbox

        return (
            (minx + maxx) / 2,
            (maxy + miny) / 2
        )

def distance(p1: tuple, p2: tuple) -> float:
    dr = p1[0] - p2[0]
    dg = p1[1] - p2[1]
    db = p1[2] - p2[2]

    return (dr**2 + dg**2 + db**2)**0.5

def get_outlines(img_path: str, seuil_distance: float = 150, display: bool = True) -> Image:
    """Renvoie une image noir et blanc (noir pour contour)"""
    img = Image.open(img_path).convert("RGBA")
    pixels = img.load()
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

            if any([distance(pixel, n) > seuil_distance for n in neighbours]):
                result.putpixel((x, y), (0, 0, 0))

    if display:
        result.show()
    
    return result

def get_regions_pixels(img: Image, min_pixels_region: int = 150, allow_cut_regions: bool = False, display: bool = True) -> Image:
    pixels = img.load()
    visited = set()
    regions = []
    if display:
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
                continue
            
            if len(region_pixels) > min_pixels_region:
                regions.append(region_pixels)
                if display:
                    for x, y in region_pixels:
                        res.putpixel((x, y), (255, 255, 255))

    if display:
        res.show()
    return regions

def display_regions(regions: list[Region], width: int = None, height: int = None) -> Image:
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

def regions_touch(r1: Region, r2: Region, pixels, img_size: tuple, display: bool = False) -> bool:
    res = Image.new("RGB", img_size)
    outline_pixels = [
        (x, y) for x, y in r1.pixels
        if any([pixels[x+var_x, y+var_y] != (255, 255, 255) for var_x in range(-1, 2) for var_y in range(-1, 2) 
                if 0 <= x + var_x < img_size[0] and 0 <= y + var_y < img_size[1]
            ])
    ]

    for pixel in outline_pixels:
        res.putpixel(pixel, (255, 0, 0))

    outline_pixels.sort(key = lambda x : ((r2.center[0] - x[0])**2 + (r2.center[1] - x[1])**2)**0.5)

    dest = r2.center

    res.putpixel((int(dest[0]), int(dest[1])), (255, 0, 0))

    pixs_r1 = set(r1.pixels)
    pixs_r2 = set(r2.pixels)

    for x, y in outline_pixels:
        cur_pos = (x, y)
        visited = set()

        while True:
            if cur_pos in pixs_r2 or cur_pos == dest:
                if display:
                    res.show()
                return True
            
            if pixels[cur_pos] == (255, 255, 255) and not cur_pos in pixs_r1: # Pixel blanc pas dans r1 ou r2
                break

            min_d = float("inf")
            next_pos = None

            for nx in range(cur_pos[0]-1, cur_pos[0]+2):
                for ny in range(cur_pos[1]-1, cur_pos[1]+2):
                    if (nx, ny) == cur_pos or (nx, ny) in visited:
                        continue

                    d = ((dest[0] - nx)**2 + (dest[1] - ny)**2) ** 0.5
                    if d < min_d:
                        min_d = d
                        next_pos = (nx, ny)
            
            if next_pos is not None:
                cur_pos = next_pos
                res.putpixel(cur_pos, (0, 255, 0))
            else:
                break

            visited.add(cur_pos)
    if display:
        res.show()
    return False

def get_graph(regions: list[Region], img: Image) -> dict:
    dic = {}
    ps = img.load()

    for idx, cur_r in bar_animation(regions, title="Création du graphe", refresh= 1,get_idx=True):
        neighbours = []
        for idx2, r2 in enumerate(regions):
            if idx == idx2:
                continue

            if collide_bbox(cur_r, r2):
                if regions_touch(cur_r, r2, ps, (img.width, img.height)):
                    neighbours.append(idx2)
        dic[idx] = neighbours
    
    return dic

def image_sha1(path: str) -> int:
    img = Image.open(path).convert("RGB").resize((512, 512))
    return hashlib.sha1(img.tobytes()).hexdigest()

def save_map(graph: dict, img: Image, regions: list[Region], original_img_path: str):
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

def load_map(img_path: str) -> dict | None:
    img_signature = image_sha1(img_path)

    try:
        with open(f"saves/{img_signature}.json") as f:
            res = json.load(f)
            res["graph"] = {int(key): value for key, value in res["graph"].items()}
            return res
    except FileNotFoundError: 
        return None

if __name__ == "__main__":
    img = get_outlines("assets/imgs/regions_france.jpg", display=False)
    regions = [Region(r) for r in get_regions_pixels(img, display=False)]
    
    display_regions(regions)
    print(get_graph(regions, img))

    assert regions_touch(regions[0], regions[1], img.load(), (img.width, img.height))