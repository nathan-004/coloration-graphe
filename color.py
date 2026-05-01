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

def color_welsh_powell(graph: Graphe):
    result = []
    nodes = sorted(list(graph.keys()), key = lambda x: len(graph[x]), reverse = True)
    color = (1, 0, 0)
    idx = 0

    while nodes:
        n = nodes[idx]
        if not(any([graph.colors[v] == color for v in graph[n]])):
            graph.colors[n] = color
            result.append({n: color})
            nodes.pop(idx)
        elif idx >= len(nodes) - 1:
            idx = 0
            color = (random.random(), random.random(), random.random())
        else:
            idx += 1

        if idx >= len(nodes):
            idx = 0

    return result

def color_dsatur(g: Graphe):
    def dsat(n):
        return len(set([
            g.colors[v] for v in g[n] if g.colors[v] is not None
        ]))

    nodes = sorted(list(g.keys()), key = lambda x: len(g[x]), reverse = True)
    colors = [(1, 0, 0)]

    if len(nodes) == 0:
        return
    
    f = nodes.pop(0)
    g.colors[f] = colors[0]
    result = [{f: colors[0]},]

    while nodes:
        n = max(nodes, key= lambda x : (dsat(x), len(g[x])))

        for col in colors:
            if all([col != g.colors[v] for v in g[n] if g.colors[v] is not None]):
                g.colors[n] = col
                break
        else:
            colors.append((random.random(), random.random(), random.random()))
            g.colors[n] = colors[-1]
        
        result.append({n: g.colors[n]})
        nodes.remove(n)
    
    return result

if __name__ == "__main__":
    g = Graphe.from_map_image("assets/imgs/regions_france.jpg")

    color_dsatur(g.graphe)
    display_graph(g.graphe)
