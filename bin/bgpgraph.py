import networkx as nx


class BGPGraph:
    def __init__(self):
        self.graph = nx.Graph()

    def update(self, record) -> bool:
        """
        Return true if graph changed.
        """
        return True
