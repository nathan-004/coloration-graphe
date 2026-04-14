from graph import Graphe
from utils import display_graph

result = Graphe.from_map_image("assets/imgs/regions_france.jpg")

print(result.graphe)
display_graph(result.graphe)