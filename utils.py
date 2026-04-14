import networkx as nx
import matplotlib.pyplot as plt

def display_graph(graphe, figsize: tuple = (8, 8)):
    G = nx.Graph()

    for node in graphe:
        G.add_node(node)
        for neighbour in graphe[node]:
            G.add_edge(node, neighbour)

    if not graphe.positions:
        pos = nx.spring_layout(G)
    else:
        pos = graphe.positions

        xs = [p[0] for p in pos.values()]
        ys = [p[1] for p in pos.values()]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        width, height = figsize

        range_x = max_x - min_x if max_x != min_x else 1
        range_y = max_y - min_y if max_y != min_y else 1

        margin = 0.1

        pos = {
            node: (
                margin * width + (x - min_x) / range_x * (width * (1 - 2 * margin)),
                margin * height + (y - min_y) / range_y * (height * (1 - 2 * margin))
            )
            for node, (x, y) in pos.items()
        }

    node_colors = [
        graphe.colors[i] if graphe.colors[i] is not None else "gray"
        for i in G
    ]

    plt.figure(figsize=figsize)
    nx.draw(
        G, pos, node_size=2000, with_labels=True, font_size=8, node_color=node_colors
    )

    plt.show()


# ----------------------------------------------------
# Loading Animations
# ----------------------------------------------------

def bar_animation(iterable, refresh: int = 50, size: int = 100, title:str = "Chargement", full_car: str = "█", empty_car: str = " ", get_idx: bool = False):
    maxn = len(iterable)
    r = 0

    for idx, el in enumerate(iterable, start=1):
        if get_idx:
            yield idx - 1, el
        else:
            yield el
        if r > refresh:
            lim = size * idx / maxn
            percent = lim / size * 100
            print(full_car * int(lim) + empty_car * int(size - lim), f"{int(percent)}% - {title}", end="\r")
            r = 0
        r += 1
    print("")

if __name__ == "__main__":
    for i in bar_animation(range(1000000)):
        pass

    for i in bar_animation(range(1000000), full_car="▰", empty_car="▱"):
        pass

    for i in bar_animation(range(1000000), full_car="■", empty_car="□"):
        pass