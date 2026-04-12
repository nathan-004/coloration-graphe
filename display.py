import networkx as nx
import matplotlib.pyplot as plt

from graph import Graphe

def display_graph(graphe:Graphe, figsize: tuple = (8, 8)) -> nx.Graph:
    G = nx.Graph()

    for node in graphe:
        for neighbour in graphe[node]:
            G.add_edge(node, neighbour)

    if not graphe.positions:
        pos = nx.spring_layout(G)
    else:
        pos = graphe.positions

    node_colors = [
        graphe.colors[i] if graphe.colors[i] is not None else "gray"
        for i in G
    ]

    plt.figure(figsize=figsize)
    nx.draw(
        G, pos, node_size=2000, with_labels=True, font_size=8, node_color=node_colors
    )

    plt.show()