from collections import defaultdict
from typing import NamedTuple

from map import *

class FromImageResult(NamedTuple):
    graphe: dict
    img: Image
    regions: list[Region]
    map_id: str

class Graphe(dict):
    """Dictionnaire de dictionnaire sous la forme {'A': 5 } contenant les voisins"""
    def __init__(self, iterable, positions: dict = {}):
        if self._is_valid_iterable(iterable):
            for key, val in iterable.items():
                self[key] = val
                
        self.colors = defaultdict(lambda : None)
        self.positions = defaultdict(lambda : None)
        self.positions.update(positions)

    def _is_valid_iterable(self, iterable: dict):
        for value in iterable.values():
            if type(value) is not list and type(value) is not dict:
                return False
        return True

    #---------------------------------------------------------
    # Méthodes spéciales
    #---------------------------------------------------------

    def __getitem__(self, key):
        if not key in self:
            self[key] = {}
        return super().__getitem__(key)
    
    def __setitem__(self, key, value: dict | list):
        if type(value) is list:
            value = {k : 1 for k in value}
        elif type(value) is not dict:
            raise TypeError(f"{type(value)} n'est pas un type valide pour la création d'un noeud")
        
        return super().__setitem__(key, value)

    #---------------------------------------------------------
    # Ajouter Elements
    #---------------------------------------------------------

    def add_arrete(self, a, b, value = 1):
        self[a][b] = value
        self[b][a] = value

    def add_arc(self, a, b, value = 1):
        self[a][b] = value

    def add_arretes(self, *arretes):
        for arrete in arretes:
            self.add_arrete(*arrete)

    #---------------------------------------------------------
    # Création Graphe
    #---------------------------------------------------------

    @staticmethod
    def from_matrice(matrice, arretes, oriente = False):
        g = Graphe()
        for a, row in zip(arretes, matrice):
            for b, v in zip(arretes, row):
                if v != 0:
                    if oriente:
                        g.add_arc(a, b, v)
                    else:
                        g.add_arrete(a, b, v)
        return g
    
    @staticmethod
    def from_map_image(img_path: str, display: bool = False) -> FromImageResult:
        map_result = load_map(img_path)

        if map_result is not None:
            print(f"Sauvegarde trouvée pour {img_path}")

            img = Image.open(map_result["img_path"])
            regions_pixels, regions_img = get_regions_pixels(img, display=display)
            return FromImageResult(
                Graphe(
                    map_result["graph"], {idx: (center[0], img.height - center[1]) for idx, center in enumerate(map_result["centers"])}
                ),
                regions_img,
                [Region(r) for r in regions_pixels],
                image_sha1(img_path)
            )

        img = get_outlines(img_path, display=display)
        regions_pixels, regions_img = get_regions_pixels(img, display=display)
        regions = [Region(r) for r in regions_pixels]

        if display:
            display_regions(regions)

        graphe = get_graph(regions, img)

        save_map(graphe, regions_img, regions, img_path)

        return FromImageResult(
            Graphe(graphe, positions= {idx: (r.center[0], img.height - r.center[1]) for idx, r in enumerate(regions)}),
            regions_img,
            regions,
            image_sha1(img_path)
        )
    
    @staticmethod
    def from_map_id(id:str, display: bool = False) -> FromImageResult:
        map_result = load_map(img_signature=id)

        if map_result is not None:
            print(f"Sauvegarde trouvée pour {id}")

            img = Image.open(map_result["img_path"])
            regions_pixels, regions_img = get_regions_pixels(img, display=display)
            return FromImageResult(
                Graphe(
                    map_result["graph"], {idx: (center[0], img.height - center[1]) for idx, center in enumerate(map_result["centers"])}
                ),
                regions_img,
                [Region(r) for r in regions_pixels],
                id
            )
    
def get_regions_france() -> Graphe:
    noms_regions = [
        "Hauts-de-France",
        "Normandie", "Île de France", "Grand Est",
        "Bretagne", "Pays de la Loire", "Centre-Val de Loire", "Bourgogne-Franche-Comté",
        "Nouvelle-Aquitaine", "Auvergne-Rhône-Alpes",
        "Occitanie", "Provence-Alpes-Côte d'Azur"
    ]

    dic_regions = {
        0: [1, 2, 3],              # Hauts-de-France
        1: [0, 2, 6, 5, 4],        # Normandie
        2: [1, 0, 3, 7, 6],        # Île de France
        3: [0, 2, 7],              # Grand Est
        4: [1, 5],                 # Bretagne
        5: [4, 1, 6, 8],           # Pays de la Loire
        6: [1, 2, 5, 7, 8, 9],     # Centre-Val de Loire
        7: [3, 2, 6, 9],           # Bourgogne-Franche-Comté
        8: [5, 6, 9, 10],          # Nouvelle-Aquitaine
        9: [7, 6, 8, 10, 11],      # Auvergne-Rhône-Alpes
        10: [8, 9, 11],            # Occitanie
        11: [9, 10]                # Provence-Alpes-Côte d'Azur
    }

    positions = {
        0: (5, 9),
        1: (3, 7),
        2: (5, 7),
        3: (7, 7),
        4: (1, 5),
        5: (3, 5),
        6: (5, 5),
        7: (7, 5),
        8: (3, 3),
        9: (6, 3),
        10: (4, 1),
        11: (7, 1)
    }

    positions = {
        noms_regions[key]: value for key, value in positions.items()
    }

    regions = {
        noms_regions[key]: [noms_regions[v] for v in value] for key, value in dic_regions.items()
    }

    return Graphe(regions, positions)