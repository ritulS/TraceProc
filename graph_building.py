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

class node_info:
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
                nodeid_map[i.um] = node_info(0,0)
            if call.dm not in nodeid_map: # rpctype applies only for dm
                nodeid_map[i.dm] = node_info(0, call.rpctype)
            elif nodeid_map[i.dm].n_type == 0:
                nodeid_map.n_type = call.rpctype

        if ctr == 1000: # exit after x traces
            break

    # Give numeric ids to all nodes
    all_nodes = nodeid_map.keys()
    for i in range(len(all_nodes)):
        nodeid_map[all_nodes[i]].num_id = i
    del all_nodes

    # Saving nodeid map and edgeslist


    # Graph building
    