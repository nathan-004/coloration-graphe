from graph import Graphe
from display import display_graph

result = Graphe.from_map_image("assets/imgs/regions_france.jpg", display=True)

print(result.graphe)
display_graph(result.graphe)