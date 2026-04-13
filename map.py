from PIL import Image, ImageDraw, ImageFont

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

    for y in range(img.height):
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

    for y in range(img.height):
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

def get_graph(regions: list[Region]) -> dict:
    dic = {}

    for idx, cur_r in enumerate(regions):
        neighbours = []
        for idx2, r2 in enumerate(regions):
            if idx == idx2:
                continue

            if collide_bbox(cur_r, r2):
                neighbours.append(idx2)
        dic[idx] = neighbours
    
    return dic

if __name__ == "__main__":
    img = get_outlines("assets/imgs/regions_france.jpg", display=False)
    regions = [Region(r) for r in get_regions_pixels(img, display=False)]
    
    display_regions(regions)
    print(get_graph(regions))