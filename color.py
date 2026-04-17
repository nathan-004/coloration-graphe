import random

from graph import Graphe

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

def color_glouton(graph: Graphe):
    r = 1
    g = 0
    b = 0
    colors = []
    noeuds = list(graph.keys())
    while noeuds:
        for i in noeuds:
            region = i
            for color in colors:
                same = False
                for voisin in graph[region]:
                    if color == graph.colors[voisin]:
                        same = True
                        break
                if same == False:
                    graph.colors[region] = color
                else:
                    r = random.random()
                    g = random.random()
                    b = random.random()
            if graph.colors[region] is None:
                color = r,g,b
                colors.append(color)
                graph.colors[region] = color
            noeuds.remove(region)