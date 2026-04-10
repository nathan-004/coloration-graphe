class Graphe(dict):
    """Dictionnaire de dictionnaire sous la forme {'A': 5 } contenant les voisins"""
    def __init__(self, iterable):
        if self._is_valid_iterable(iterable):
            for key, val in iterable.items():
                self[key] = val

    def _is_valid_iterable(self, iterable: dict):
        for value in iterable.values():
            if type(value) is not list and type(value) is not dict:
                return False
        return True

    #---------------------------------------------------------
    # Méthodes spéciales
    #---------------------------------------------------------

    def __getitem__(self, key):
        if not key in self:
            self[key] = {}
        return super().__getitem__(key)
    
    def __setitem__(self, key, value: dict | list):
        if type(value) is list:
            value = {k : 1 for k in value}
        elif type(value) is not dict:
            raise TypeError(f"{type(value)} n'est pas un type valide pour la création d'un noeud")
        
        return super().__setitem__(key, value)

    #---------------------------------------------------------
    # Ajouter Elements
    #---------------------------------------------------------

    def add_arrete(self, a, b, value = 1):
        self[a][b] = value
        self[b][a] = value

    def add_arc(self, a, b, value = 1):
        self[a][b] = value

    def add_arretes(self, *arretes):
        for arrete in arretes:
            self.add_arrete(*arrete)

    #---------------------------------------------------------
    # Création Graphe
    #---------------------------------------------------------

    @staticmethod
    def from_matrice(matrice, arretes, oriente = False):
        g = Graphe()
        for a, row in zip(arretes, matrice):
            for b, v in zip(arretes, row):
                if v != 0:
                    if oriente:
                        g.add_arc(a, b, v)
                    else:
                        g.add_arrete(a, b, v)
        return g