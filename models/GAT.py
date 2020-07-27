import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import torch
import torch.nn as nn
import torch.nn.functional as F

from layers.graph_attention_layer import GraphAttentionLayer
from readouts.basic_readout import readout_function

"""
Base paper: https://arxiv.org/abs/1710.10903
"""

class GAT(nn.Module):
    def __init__(self, n_feat, n_class, n_layer, agg_hidden, fc_hidden, dropout, readout, device):
        super(GAT, self).__init__()

        self.n_layer = n_layer
        self.dropout = dropout
        self.readout = readout
        
        # Graph Attention Layer
        self.attentions = [GraphAttentionLayer(n_feat, agg_hidden, self.dropout, device) for _ in range(n_layer)]
        for i, attention in enumerate(self.attentions):
            self.add_module('attention_{}'.format(i), attention)
                    
        # Fully-connected layer
        self.fc1 = nn.Linear(agg_hidden*n_layer, fc_hidden)
        self.fc2 = nn.Linear(fc_hidden, n_class)
        
    def forward(self, data):
        x, adj = data[:2]
        
        # Dropout        
        x = F.dropout(x, p=self.dropout, training=self.training)
        
        # Graph Attention Layer
        x = torch.cat([att(x, adj) for att in self.attentions], dim=2)

        # Readout
        x = readout_function(x, self.readout)
        
        # Fully-connected layer
        x = F.relu(self.fc1(x))
        x = F.softmax(self.fc2(x))
        
        return x

    def __repr__(self):
        layers = ''
        
        for i in range(self.n_layer):
            layers += str(self.attentions[i]) + '\n'
        layers += str(self.fc1)
        layers += str(self.fc2)
        return layers