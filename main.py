from graph import Graphe
from display import display_graph

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

g = Graphe(regions, positions)
print(g)

display_graph(g)