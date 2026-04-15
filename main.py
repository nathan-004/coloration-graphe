from graph import Graphe, get_regions_france
from utils import display_graph
import random

#colorisation purement aléatoire
def color_random(graph: Graphe):
    noeuds = list(graph.keys())
    while noeuds:
        region = random.choice(noeuds)
        color = random.random(),random.random(),random.random()
        graph.colors[region] = color
        noeuds.remove(region)

#result = Graphe.from_map_image("assets/imgs/regions_france.jpg")

graph = get_regions_france()
graph.colors["Hauts-de-France"]= 1,1,0.7


color_random(graph)
display_graph(graph)

