[Flask rendering templates](https://flask.palletsprojects.com/en/stable/quickstart/#rendering-templates)

### To Do

- [ ] Optimisation
  - [X] Enlever chargement régions côté serveur
  - [X] Créer cache pixels région (client)
- [X] Algorithmes de coloration
- [X] Mettre les régions coupées en bleu

### Lancer le projet

Lancer plusieurs aura différents effets :
- `color.py` permet de voir la coloration des graphes
- `map.py` permet de voir le processus de passage d'une image à une carte coloriable
- `main.py` permet de lancer le serveur web

⚠ Attention : Certaines fonctionnalités du programme ne sont pas fonctionnels sur EduPython ou les ordinateurs du lycée. Parmi elles : l'animation textuelle de progrès et la suppression des fichiers temporaires dans `assets/temp`.

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

Les erreurs arrivaient surtout en détéctant que deux régions étaient limitrophes alors qu'elles étaient séparées par une autre région. Pour prouver que deux régions étaient limitrophes de manière plus sûre, j'ai utilisé la dilatation sur l'image. Elle consiste à faire passer chaque pixels noir de l'image en blanc si au moins de ses voisins est blanc. Et en regardant les pixels communs aux régions, on voit celles qui étaient séparés par un contour. Mais le problème est que la dilatation ne transforme que la première couche des contours. Or, si l'épaisseur du contour dépasse 1, ça ne fonctionne pas, c'est pour ça que je répète cette opération un certain nombre de fois. Mais comme on peut le voir avec `pays_afrique.webp`, ça peut causer quelques problèmes puisque c'est une constante et elle n'est pas encore choisie en fonction de l'image. 

On obtient ainsi un graphe qui n'a plus qu'à être colorié.

##### Coloriage Graphe

Pour colorier le graphe, nous avons mis les différents algorithmes de coloration présents sur [ce site](https://hmalherbe.fr/thalesm/gestclasse/documents/Terminale_NSI/2021-2022/TP/Projets/Graphes/Coloration_graphes_cartes_geographiques.html).

Pour ma part j'ai réalisé l'algorithme de Welsh-Powell et celui de DSATUR. L'algorithme de Welsh-Powell consiste à colorier d'abord les sommets ayant le plus de voisins (le degré maximal) puisqu'ils seront les plus difficiles à colorier ensuite. Alors que l'algorithme de DSATUR commence par les sommets les plus saturés (ceux ayant le plus de voisins coloriés). Les deux sont plutôt similaires mais ne maximisent pas la même valeur.

Ainsi colorié, il fallait maintenant colorier l'image et la montrer à l'utilisateur.

##### Interface

Pour l'interface, nous avons opté pour une interface web pour la vitesse supérieure du javascript pour permettre des animations plus rapides et pour suivre l'exemple du site demandé. 

Il a donc fallu établir une connection entre l'interface et le backend python. J'ai pour cela utilisé Flask pour sa simplicité. Puis il a fallu connecter l'interface lors des différentes étapes du coloriage de la carte.

D'abord le chargement de l'image, qui est la partie la plus longue, pour améliorer l'expérience utilisateur, j'ai donc crée une sauvegarde minimale du traitement exécuté lors du chargement de l'image en ne sauvegardant que l'image à colorier, les centres des régions et les liens entre celles-ci et en laissant de côté les pixels de chaque région (qui prendraient beaucoup trop de place). Ainsi à chaque upload, on regarde si le sha1 de l'image (permet de vérifier que c'est la même image sans avoir à vérifier toute l'image et sans regarder le chemin par exemple) est déjà sauvegardé, et s'il l'est, on ne calcule rien.

Ensuite on peut amener l'utilisateur sur la page de la carte en question, où nous nous sommes inspirés du choix de l'algorithme pour l'interface, dans lequel l'utilisateur peut choisir l'algorithme qu'il veut éxécuter. Lors de cette saisie, le frontend demande les étapes de coloration dans l'ordre. Il va ensuite les relier aux centres qu'il a déjà récupéré pour colorier la carte.

Pour colorier la carte, il éxécute l'algorithme Flood fill vu précedemment en commençant par le centre de la région (qui peut poser certains problèmes selon la forme de la région).

##### Améliorations

D'abord la résolutions de problèmes telles que des faux négatifs dans la détection des régions lorsque les régions sont trop petites, il faudrait ajuster l'aire minimale d'une région en fonction de la taille moyenne ou en fonction de la taille de l'image et du nombre de région obtenue ? Aussi des problèmes de détections de régions limitrophes dans le cas de contours trop épais.

Ensuite l'ajout d'un algorithme de sélection des terres et des mers / océans plus poussés, pour l'instant ce n'est que regarder si une région touche le bord de l'image. Aussi ajouter plus de possibilités de customisation du résultat dans l'upload d'une image notamment. Et enfin faire la page `Voir cartes déjà existantes` et ajouter un bouton autoplay de l'animation de coloriage. 
