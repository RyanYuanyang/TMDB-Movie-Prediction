import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from Hypergraph_utils import *
from torch.nn.parameter import Parameter
from models import paramHelper


class HGNN_conv(nn.Module):
    def __init__(self, ph, in_dim, out_dim) -> None:
        super().__init__()
        self.weights = Parameter(torch.Tensor(in_dim, out_dim)).to(ph.device)
        self.biases = Parameter(torch.Tensor(out_dim)).to(ph.device)

        stdv = 1. / math.sqrt(self.weights.size(1))
        self.weights.data.uniform_(-stdv, stdv)
        self.biases.data.uniform_(-stdv, stdv)

    def forward(self, x: torch.Tensor, G: torch.Tensor) -> None:
        x = x @ self.weights + self.biases # fc
        x = G @ x # conv
        return x
    
class HGNN_oneCh(nn.Module):
    def __init__(self, ph, in_dim, hid_dim, out_dim, dropout=0.5) -> None:
        super().__init__()
        self.dropout = dropout
        self.hgnnconv1 = HGNN_conv(ph, in_dim, hid_dim)
        self.hgnnconv2 = HGNN_conv(ph, hid_dim, out_dim)

    def forward(self, x, G):
        x = self.hgnnconv1(x, G)
        x = F.leaky_relu(x)
        x = F.dropout(x, self.dropout)
        x = self.hgnnconv2(x, G)
        return x

class Fuser(nn.Module):
    def __init__(self, ph, ch_dim=2, num_ch=6) -> None:
        super().__init__()
        self.in_dim = ch_dim * num_ch
        self.voter = nn.Linear(self.in_dim, 1).to(ph.device)

    def forward(self, x):
        return self.voter(x).squeeze()


class Model(nn.Module):
    def __init__(self, ph, ch_indim=19, ch_latdim=8, ch_outdim=1, num_ch=6) -> None:
        super().__init__()
        self.num_ch = num_ch
        self.channels = nn.ModuleList([HGNN_oneCh(ph, ch_indim, ch_latdim, ch_outdim, dropout=ph.dropout) for _ in range(num_ch)])
        self.fuser = Fuser(ph, ch_dim=ch_outdim, num_ch=num_ch)
        self.channels_rets = []

    def forward(self, x:torch.tensor, Gs: list):
        self.channels_rets = []
        for i in range(self.num_ch):
            voteCandidate = self.channels[i].forward(x, Gs[i])
            self.channels_rets.append(voteCandidate)
        voteReady = torch.cat(self.channels_rets, dim=1)
        output = self.fuser(voteReady)
        return output

