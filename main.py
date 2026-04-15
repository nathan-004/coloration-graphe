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


#colorisation aléatoire avec règles de colorisation
def color_random_rules(graph: Graphe):
    colors = []
    noeuds = list(graph.keys())
    while noeuds:
        region = random.choice(noeuds)
        for color in colors:
            same = False
            for voisin in graph[region]:
                if color == graph.colors[voisin]:
                    same = True
                    break
            if same == False:
                graph.colors[region] = color
                break
        if graph.colors[region] is None:
            color = random.random(), random.random(), random.random()
            colors.append(color)
            graph.colors[region] = color
        noeuds.remove(region)







graph = get_regions_france()

#color_random(graph)
color_random_rules(graph)

display_graph(graph)

