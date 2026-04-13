from PIL import Image

from random import choice
from collections import deque

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

def get_regions(img: Image, min_pixels_region: int = 150, allow_cut_regions: bool = False, display: bool = True) -> Image:
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

    res.show()
    return regions

if __name__ == "__main__":
    img = get_outlines("assets/imgs/regions_france.jpg")
    regions = get_regions(img)
    print(len(regions))