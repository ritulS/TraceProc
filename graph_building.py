import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import pygsp as pygsp
from pygsp import graphs, filters, reduction

from tqdm import tqdm
import numpy as np
import os

class Trace:
    def __init__(self):
        self.calls = []

class Node_info:
    def __init__(self, num_id, n_type):
        self.num_id = num_id
        self.n_type = n_type

class Call:
    def __init__(self, traceid, timestamp, rpcid, um, dm, rpctype, interface, rt):
        self.traceid = traceid
        self.timestamp = timestamp
        self.rpcid = rpcid
        self.um = um
        self.dm = dm 
        self.rpctype = rpctype
        self.interface = interface
        self.rt = rt
    def string(self):
        return self.traceid + "," + str(self.timestamp) + "," + self.rpcid + "," + self.um + "," + self.dm + "," +\
            self.rpctype + "," + self.interface + "," + str(self.rt)

def csv_to_df(file: str):
    df = pd.read_csv(file)
    return df

def extract_traceid_rows(df, tid):
    f_df = df[df['traceid'] == tid]
    tid_calls = [
        Call(
            str(row.traceid), 
            int(row.timestamp), 
            str(row.rpcid), 
            str(row.um), 
            str(row.dm), 
            str(row.rpctype), 
            str(row.interface), 
            int(row.rt)
        ) for row in f_df.itertuples(index=False)
    ]
    return tid_calls

def plot_graphnx(G, pos=None, edge_width=0.8, node_size=20, alpha=0.55, title=""):
    """
    Plot a single graph G using networkx.
    pos : dict, optional
        A dictionary with nodes as keys and positions as values.
        If not provided, will use spring layout.

    """
    if pos is None:
        pos = nx.spring_layout(G)

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(1, 1, 1, projection='3d' if len(next(iter(pos.values()))) == 3 else None)
    ax.axis("off")
    ax.set_title(title)

    # Draw edges and nodes
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=alpha, width=edge_width)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_size, alpha=alpha)

    fig.tight_layout()
    plt.savefig("test.png", format='png')
    plt.close(fig)

    return fig


def main():
    # Extract to dataframe
    df = csv_to_df("./MSCallGraph_0.csv")

    # Extract all tids
    tids_list = df['traceid'].unique()
    print("Num of tids: ", len(tids_list))

    # Create edges & nodes list
    all_edges = []
    all_nodes = []
    nodeid_map = {} # nodeid mappings to numeric indices & type
    ctr = 0
    for i in tqdm(range(len(tids_list))):
        ctr += 1
        tid_calls = extract_traceid_rows(df, tids_list[i])
        for call in tid_calls:
            all_edges.append([call.um, call.dm]) # creating edge
            if call.um not in nodeid_map:
                nodeid_map[call.um] = Node_info(0,0)
            if call.dm not in nodeid_map: # rpctype applies only for dm
                nodeid_map[call.dm] = Node_info(0, call.rpctype)
            elif nodeid_map[call.dm].n_type == 0:
                nodeid_map[call.dm].n_type = call.rpctype

        if ctr == 100: # exit after x traces
            break

    # Give numeric ids to all nodes
    all_nodes = list(nodeid_map.keys())
    num_nodes = len(all_nodes)
    for i in range(len(all_nodes)):
        nodeid_map[all_nodes[i]].num_id = i
    del all_nodes
    # print(nodeid_map)

    # Saving nodeid map and edgeslist


    # Graph building (networkx)
    G = nx.Graph()
    G.add_edges_from(all_edges)
    plot_graphnx(G)
    adjacency_matrix = nx.adjacency_matrix(G).todense()
    G_pygsp = graphs.Graph(adjacency_matrix)

    # Graph building (pygsp)
    # all_edges_numeric = []
    # for i in all_edges:
    #     i[0] = nodeid_map[i[0]].num_id
    #     i[1] = nodeid_map[i[1]].num_id


if __name__ == '__main__':
    main()
