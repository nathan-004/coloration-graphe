from PIL import Image

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

if __name__ == "__main__":
    get_outlines("assets/imgs/regions_france.jpg")