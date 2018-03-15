"""Density Tree Creation"""
import numpy as np
from .density_tree import DensityNode
from .helpers import entropy_gaussian, get_best_split, split

def create_density_tree(dataset, dimensions, clusters, parentnode=None, side_label=None, verbose=False):
    """create decision tree be performing initial split,
    then recursively splitting until all labels are in unique bins
    init: flag for first iteration
    Principle:  create an initial split, save value, dimension, and entropies on node as well as on both split sides
    As long as total number of splits < nclusters - 1, perform another split on the side having the higher entropy
    Or, if there are parent nodes: perform a split on the side of the node that has the highest entropy on a side
    """
    # verbose
    if verbose:
        print("Creating node (%i remaining)" % (clusters-1))
    
    treenode = DensityNode()
        
    # split
    if parentnode is not None: # if we are not at the first split
        # link parent node to new node
        treenode.parent = parentnode
        if side_label == 'left':
            treenode.parent.left = treenode
        else:
            treenode.parent.right = treenode
        
        # get subset of data at this level of the tree
        dataset_node = treenode.get_dataset(None, dataset)
            
    else: # first split
        dataset_node = dataset
        
    dim_max, val_dim_max, _, _ = get_best_split(
        dataset_node, labelled=False, verbose=verbose)
    left, right, e_left, e_right = split(
        dataset_node, dim_max, val_dim_max, get_entropy=True)

    # save tree node
    treenode.split_dimension = dim_max
    treenode.split_value = val_dim_max
    treenode.left_dataset_pct = len(left) / len(dataset)
    treenode.right_dataset_pct = len(right) / len(dataset)
    treenode.entropy = entropy_gaussian(dataset_node)
    treenode.cov = np.cov(dataset_node.T)
    
    treenode.mean = np.mean(dataset_node, axis=0)
    treenode.left_cov = np.cov(left.T)
    treenode.left_mean = np.mean(left, axis=0)
    treenode.right_cov = np.cov(right.T)
    treenode.right_mean = np.mean(right, axis=0)
    treenode.left_entropy = e_left
    treenode.right_entropy = e_right

    clusters_left = clusters - 1
    if clusters_left > 1:
        # recursively continue splitting
        # continue splitting always splitting on worst side (highest entropy)
        # find node where left or right entropy is highest and left or right node is not split yet
        node_e, e, side = treenode.get_root().highest_entropy(None, 0, 'None')

        create_density_tree(dataset, dimensions, clusters=clusters_left,
                            parentnode=node_e, side_label=side, verbose=verbose)  
    return treenode