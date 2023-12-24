import torch
import torch.optim as optim
import torch.nn.functional as F
import pandas as pd
import pandas
import time
import os
from tqdm import tqdm
from Hypergraph_utils import *
from models.paramHelper import paramHelper
from models.HGNN import Model
from train_utils import *
import matplotlib.pyplot as plt


helper = paramHelper(max_epoch=500, n_batch=1, dropout=0)

mean_train_loss = 0
write = []

torch.cuda.empty_cache()

for batch_idx in range(helper.n_batch):
    model = Model(helper, ch_latdim=30, ch_outdim=9)

    readyGs = Gs('genres production_companies production_countries Keywords cast crew'.split(), helper, batch_idx, print_start_end=False)

    d = fineBatchInfo(helper, batch_idx)
    batchCombTrainOnlyData = d['allDataFullPass'][d['trainOnlyIdxs']]
    batchCombTrainOnlyLabel = d['allLabelFullPass'][d['trainOnlyIdxs']]
    batchCombData = d['allDataFullPass'][d['batchCombIdxs']]
    batchCombLabel = d['allLabelFullPass'][d['batchCombIdxs']]
    batchCombIdxs = d['batchCombIdxs']
    batchTrainOnlyIdxs = d['trainOnlyIdxs']
    batchTestOnlyIdxs = d['testOnlyIdxs']

    optimizer = optim.Adam(model.parameters(), lr=helper.lr)
    criterion = torch.nn.MSELoss()

    since = time.time()

    model.train()

    losses = []

    for epoch in tqdm(range(helper.max_epoch)):
        optimizer.zero_grad()

        outputs = model(batchCombData, readyGs)

        loss = criterion(batchCombTrainOnlyLabel, outputs[batchTrainOnlyIdxs])
        losses.append(loss.item())
        loss.backward()
        optimizer.step()
    
    time_cost = time.time() - since
    mean_train_loss += losses[-1] / helper.n_batch

    temp = list(map(lambda x: torch.expm1(x).item(), outputs[batchTrainOnlyIdxs.shape[0]:]))
    write += temp

write_df = pd.DataFrame(columns=['id', 'revenue'], index=None)
write_df.loc[:,'id'] = list(range(3001, 7399))
write_df.loc[:,'revenue'] = write
write_df.to_csv('submission.csv', index=None)