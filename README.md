[Flask rendering templates](https://flask.palletsprojects.com/en/stable/quickstart/#rendering-templates)

### To Do

- [ ] Optimisation
  - [X] Enlever chargement régions côté serveur
  - [X] Créer cache pixels région (client)
- [X] Algorithmes de coloration
- [X] Mettre les régions coupées en bleu

### Compte Rendu

L'objectif était de créer une interface utilisateur permettant de montrer différents algorithmes de coloration de graphes en action. Pour cela il a fallu se poser plusieurs questions, la première étant d'avoir une carte que l'on pouvait colorier.

##### Stockage et coloriage de la carte

Notre regard s'est d'abord porté vers les json de cartes présents gratuitement en ligne que l'on pourrait afficher sur une carte folium par exemple. Mais le problème était que pour chaque cartes, il fallait stocker des données très lourdes (> 1Go). Pour éviter ce problème et faciliter l'importation de cartes, nous nous somme dirigés vers une entrée sous forme d'image. 

Le coloriage se ferait ainsi en prenant un point d'une région et de visiter tous les voisins et de recommencer jusqu'à tomber sur un contours ([Flood Fill Algorithm](https://en.wikipedia.org/wiki/Flood_fill)). Or, pour réaliser ceci, il nous fallait une image avec de préférence deux couleurs (blancs pour l'intérieur des régions et noir pour les contours) ou au moins une couleur certaine pour les contours. Mais les images en entrée ne l'étaient pas forcément, il a donc fallu créer cette image en noir et blanc avec le blanc signifiant remplissable et le noir ou autre couleur signifiant l'inverse.

Pour créer cette image, il fallait d'abord connaître les pixels qui étaient remplissables et ceux qui ne l'étaient pas — ceux qui étaient l'intérieur d'une région et ceux qui étaient des contours. J'ai donc crée une nouvelle image avec comme valeur de pixel soit noir si il y avait une grande différence entre la couleur du pixel et celle d'au moins un de ses voisins est supérieure à un seuil définie auparavant. Maintenant que l'on a une image binaire (deux couleurs), on peut détecter les régions plus facilement.

Pour détecter les régions, on utilise le même algorithme que le coloriage, le flood fill : On va d'abord marquer tous les pixels comme non-visités, et pour chaque pixel sur l'image, s'il n'est pas déjà visité, on va étendre la recherche à ses voisins récursivement jusqu'à atteindre un contour. Ainsi, on aura une liste des pixels présents dans la région du pixel que l'on visite qu'on ajoute au résultat. Or, sur la carte de France, environ 6000 régions étaient détectés, en effet, en zoomant bien, on pouvait observer des pixels blancs (qui sont remplissable) isolés dans les contours. Il a donc fallu rajouter un filtre sur l'aire de la région puis ensuite sur la bbox des régions pour détecter s'il n'y avait pas des traits très fins qui pouvaient apparaître si les contours de l'image d'origine étaient trop épais.

Maintenant on a une image des régions coloriables en blancs et des contours en noir. Mais il faut encore appliquer un algorithme de coloration dessus donc la transformer en graphe.

##### Conversion carte -> Graphe

Pour passer du liste de régions à un graphe, il fallait deux éléments : les régions, les liens entres les régions. On avait la première et il nous manquait la deuxième. Pour trouver les liens entre les régions, il a fallu voir si elles étaient adjacentes.

La première solution a été de faire la collision non sur les formes complexes des différentes régions mais plutôt sur les bbox des régions ou le carré minimal dans lequel elles peuvent rentrer. La collision de deux carrés étant simple et rapide. Or, il y a rapidement eu des problèmes, les bbox peuvent être imprécises, elles peuvent largement augmenter la surface de la région si la région a des extrémités très éloignées mais inéquilibrées, et le graphe était faussé par ce détail. Il a donc fallu faire des calculs plus complexes.

Les erreurs arrivaient surtout en détéctant que deux régions étaient limitrophes alors qu'elles étaient séparées par une autre région. Pour prouver que 