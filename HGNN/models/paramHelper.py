import os
import time
import copy
import torch
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import pandas as pd

entire_df_read = pd.read_csv('entire.csv', encoding='utf-8-sig')

class paramHelper:
    def __init__(self, entire_df=entire_df_read, lr=1e-1, n_batch=4, max_epoch=150, dropout=0.5) -> None:
        self.lr = lr
        self.dropout = dropout
        self.max_epoch = max_epoch
        self.n_batch = n_batch
        self.entire_df = entire_df
        self.batchCombIdxses = []
        self.trainOnlyIdxses = [] # acccess by fineBatchInfo()
        self.testOnlyIdxses = [] # acccess by fineBatchInfo()
        self.trainsize = 0
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.construct_data()

    def construct_data(self):
        idx_allpass = torch.arange(self.entire_df.shape[0])
        train_only_idxs = torch.nonzero(torch.from_numpy(np.array(entire_df_read.revenue != -1))).squeeze(dim=1)
        self.trainsize = train_only_idxs.shape[0]
        test_allpass = torch.nonzero(torch.from_numpy(np.array(entire_df_read.revenue == -1))).squeeze(dim=1)
        testbatchsize = test_allpass.shape[0] // self.n_batch + 1
        for i in range(self.n_batch):
            if i != self.n_batch - 1:
                testidxs_onebatch = test_allpass[torch.arange(i*testbatchsize, (i+1)*testbatchsize)]
            else:
                testidxs_onebatch = test_allpass[torch.arange(i*testbatchsize, test_allpass.shape[0])]

            self.trainOnlyIdxses.append(train_only_idxs)
            self.trainOnlyIdxses[-1].to(self.device)

            self.testOnlyIdxses.append(testidxs_onebatch)
            self.testOnlyIdxses[-1].to(self.device)

            self.batchCombIdxses.append(torch.cat((train_only_idxs, testidxs_onebatch)))
            self.batchCombIdxses[-1].to(self.device)
            