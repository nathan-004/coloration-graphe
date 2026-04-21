import random

from graph import Graphe
from utils import display_graph

#colorisation purement aléatoire
def color_random(graph: Graphe):
    result = []
    noeuds = list(graph.keys())

    while noeuds:
        region = random.choice(noeuds)
        color = random.random(),random.random(),random.random()
        graph.colors[region] = color
        noeuds.remove(region)
        result.append({region: color})

    return result

#colorisation aléatoire avec règles de colorisation
def color_random_rules(graph: Graphe):
    result = []
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
        result.append({region: color})
        noeuds.remove(region)

    return result

def color_glouton(graph: Graphe):
    result = []
    color = random.random(), random.random(), random.random()
    noeuds = list(graph.keys())

    while noeuds:
        r = None
        v_max = -float("inf")

        for i in noeuds:
            n = 0 # Nombre de voisins non coloriés

            for voisin in graph[i]:
                if graph.colors[voisin] is None:
                    n+=1
                elif graph.colors[voisin] == color:
                    break
            else:
                if v_max <= n :
                    v_max = n
                    r = i

        if r is None:
            color = random.random(), random.random(), random.random()
            continue

        result.append({r: color})
        graph.colors[r] = color
        noeuds.remove(r)

    return result


if __name__ == "__main__":
    g = Graphe.from_map_image("assets/imgs/regions_france.jpg")

    color_glouton(g.graphe)
    display_graph(g.graphe)
