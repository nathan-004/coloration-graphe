"""
Auteurs: Hugo, Nathan
Permet de colorier les graphes suivant différents algorithmes
"""

import random

from graph import Graphe
from utils import display_graph

#colorisation purement aléatoire (hugo)
def color_random(graph: Graphe):
    result = []
    noeuds = list(graph.keys()) #"noeuds" = la liste de toute les clés présnente dans graph (nos régions)

    while noeuds: #tant que la liste n'est pas vide
        region = random.choice(noeuds) #"region" = une région aléatoire parmis toute les régions stocker dans noeuds
        color = random.random(),random.random(),random.random() #couleur aléatoire
        graph.colors[region] = color #on color la région
        noeuds.remove(region) #on retire la région coloré
        result.append({region: color}) #stock le résultat

    return result

#colorisation aléatoire avec règles de colorisation (hugo)
def color_random_rules(graph: Graphe):
    result = []
    colors = []
    noeuds = list(graph.keys()) #"noeuds" = la liste de toute les clés présnente dans graph (nos régions)

    while noeuds: #tant que la liste n'est pas vide
        region = random.choice(noeuds) #"region" = une région aléatoire parmis toute les régions stocker dans noeuds
        for color in colors:
            same = False # la couleur n'est pas la même
            for voisin in graph[region]:
                if color == graph.colors[voisin]: #demande si la couleur du voisin est la même que la couleur actuelle
                    same = True #c'est vraie même couleur
                    break
            if same == False: #si pas la même couleur
                graph.colors[region] = color #on color la région
                break
        if graph.colors[region] is None: #si aucune couleur est existante
            color = random.random(), random.random(), random.random() #on créer une couleur aléatoire
            colors.append(color)
            graph.colors[region] = color #on color la région
        result.append({region: color}) #stock le résultat
        noeuds.remove(region) #on enlève la région coloré

    return result

def color_glouton(graph: Graphe): #(hugo)
    result = []
    color = random.random(), random.random(), random.random() #couleur aléatoire
    noeuds = list(graph.keys()) #"noeuds" = la liste de toute les clés présnente dans graph (nos régions)

    while noeuds: #tant que la liste n'est pas vide
        region = None
        v_max = -1 # Nombre de voisins non coloriés maximum

        for i in noeuds: #pour le nombre de région
            n = 0 # Nombre de voisins non coloriés

            for voisin in graph[i]:
                if graph.colors[voisin] is None: #si le voisin n'est pas colorié
                    n+=1 #nombre de voisin non coloré +1
                elif graph.colors[voisin] == color: #si voisin = la couleur choisi
                    break
            else:
                if v_max <= n : # si le Nombre de voisins non coloriés maximum est inférieur au nombre de voisins non colorié
                    v_max = n #Nombre de voisins non coloriés maximum = Nombre de voisins non coloriés
                    region = i #region = region la plus eloigniée

        if region is None: #si la region n'est pas coloré
            color = random.random(), random.random(), random.random() #couleur aléatoire
            continue

        result.append({region: color})
        graph.colors[region] = color #on color la région
        noeuds.remove(region) #on enlève la région coloré

    return result

def color_welsh_powell(graph: Graphe):
    result = []
    nodes = sorted(list(graph.keys()), key = lambda x: len(graph[x]), reverse = True) # Trier les sommets en fonction de leur degré
    color = (1, 0, 0)
    idx = 0

    while nodes:
        n = nodes[idx]
        if not(any([graph.colors[v] == color for v in graph[n]])): # Aucun des voisins n'a la même couleur
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
    def dsat(n): # Fonction de calcul de la saturation
        return len(set([
            g.colors[v] for v in g[n] if g.colors[v] is not None
        ]))

    nodes = sorted(list(g.keys()), key = lambda x: len(g[x]), reverse = True) # Tri par degré
    colors = [(1, 0, 0)]

    if len(nodes) == 0:
        return

    f = nodes.pop(0)
    g.colors[f] = colors[0]
    result = [{f: colors[0]},]

    while nodes:
        n = max(nodes, key= lambda x : (dsat(x), len(g[x]))) # Trouver le dsat maximum ou le degré en cas d'égalité

        for col in colors:
            if all([col != g.colors[v] for v in g[n] if g.colors[v] is not None]): # Vérifier que voisins n'ont pas la même couleur
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

    color_glouton(g.graphe)
    display_graph(g.graphe)
