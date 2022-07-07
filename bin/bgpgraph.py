import time
import networkx as nx
import matplotlib.pyplot as plt


class BGPGraph:
    def __init__(self):
        self.graph = nx.Graph()
        self.cpt = 0
        
    def get(self,
            as_numbers=None,
            prefixes=None,
            match_type="more",
            countries=None
            ):
        pass
    

    def filter_edge(self, n1, n2):
        return not (self.graph[n1][n2]["prefix"] == self.del_prefix)

    def update(self, record) -> bool:
        """
        Insert or delete paths in the graph.
        Return true if graph changed.
        """
        return True
        self.cpt += 1
        if record.type == "A":
            # Node attributes : prefix, time
            nx.add_path(
                self.graph,
                record.fields["as-path"].split(),
                **{
                record.fields["prefix"] : record.time,
                "source": record.source,
                }
            )
            nx.set_node_attributes(
                self.graph, {record.source: {record.fields["prefix"]: record.time}}
            )
        else:
            # remove path
            # check if edge has any prefix/ as ? if yes remove the edge
            self.del_prefix = record.fields["prefix"]

            for n,v in self.graph.nodes(data=True):
                if self.graph.edges[record.fields['prefix']]:
                    del self.graph.edges[n][v]

            # for self.graph.edges()
            #view = nx.subgraph_view(self.graph, filter_edge=self.filter_edge)
            #for e in view.edges():
            #    print
            #print(self.graph)
            #print(view)
            #nx.draw(view, with_labels=True, font_weight="bold")
            #nx.draw_shell(view, with_labels=True, font_weight="bold")
            #plt.show()
            #time.sleep(10)

        return True

        # Check if graph is updated
        """
        if self.cpt == 100:
            nx.draw(self.graph, with_labels=True, font_weight='bold')
            nx.draw_shell(self.graph, with_labels=True, font_weight='bold')
            plt.show()
            time.sleep(10)
            exit(0)
        """
