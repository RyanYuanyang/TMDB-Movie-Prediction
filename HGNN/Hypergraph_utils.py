import torch
import pandas as pd
import pandas
import re
import time
import os
from train_utils import fineBatchInfo
from models.paramHelper import paramHelper

entire_df_read = pd.read_csv('entire.csv', encoding='utf-8-sig')
default_n_edge_reserved=100
default_params={'Keywords':100, 'production_companies':64}

if not os.path.exists('./fineGs/'):
    os.makedirs('./fineGs/')
# genres production_companies production_countries Keywords cast crew

def clean(x: str) -> str:
    '''tool func'''
    x = x.replace('[null]', '[]').replace('null', '""').replace('[[]]', r'[]').replace('None', "'None'").replace('true', 'True').replace('false', 'False')
    x = re.sub(r"'name':'[^,]*'[^,]*'","'name':'omitted'", x)
    x = re.sub(r"'character':'[^,]*'[^,]*'","'character':'omitted'", x)
    x = re.sub(r"'character':'[^,]*'[^,]*'[^,]*'","'character':'omitted'", x)
    # if "'id':" not in x:
    #     x = x.replace("'name':", "'id':")
    return x

def makeUpId(column_name: str, onedict: set) -> int:
    if column_name == 'production_countries':
        return (ord(onedict['iso_3166_1'][0])-65)*26 + ord(onedict['iso_3166_1'][1])-65

def all_ids_and_frequency(column_name:str, train_df: pd.DataFrame=entire_df_read, n_edge_reserved=default_n_edge_reserved, print_start_end=False) -> list:
    if print_start_end:
        print('calculating all_ids_and_frequency:', column_name)
    seriesAsLst = list(map(lambda x: eval(clean(x)), list(train_df[column_name].fillna(r'[]'))))
    wanted_jobs = ('DIRECTOR', 'PRODUCER')
    weightFunc = lambda t: (6-t[1] if t[1] < 6 else 0) if column_name=='cast' else (1 if column_name != 'crew' else (1 if t[2].upper() in wanted_jobs else 0))
    s = dict()
    for dictlist in seriesAsLst:
        for onedict in dictlist:
            if 'id' in onedict:
                cid = int(onedict['id'])
            else:
                cid = makeUpId(column_name, onedict)
            order = int(onedict['order']) if column_name == 'cast' else None
            job = onedict['job'] if column_name == 'crew' else None
            if cid not in s:
                s[cid] = weightFunc((cid, order, job))
            else:
                s[cid] += weightFunc((cid, order, job))
    st = tuple(map(lambda x: (x, s[x]), s))
    strd = sorted(st, key=lambda x: x[1], reverse=True)
    ret = [ele for ele in strd if ele[1] > 1]
    if print_start_end:
        print('finished all_ids_and_frequency:', column_name)
    return ret

def one_hot_encode(column_name:str, n_reserved:int=0, train_df:pd.DataFrame=entire_df_read) -> torch.Tensor:
    if n_reserved == 0:
        n_reserved = default_params[column_name]
    ele_reserved = all_ids_and_frequency(column_name, train_df)[:n_reserved]
    encodes = torch.zeros((train_df.shape[0], len(ele_reserved)))
    rawlst = list(map(lambda x: eval(clean(x)), list(train_df[column_name].fillna(r'[]'))))
    for i in range(train_df.shape[0]):
        idlist = list(map(lambda x: int(x['id']), rawlst[i]))
        for rsvd_idx in range(len(ele_reserved)):
            if ele_reserved[rsvd_idx][0] in idlist:
                encodes[i][rsvd_idx] = 1
    return encodes

def allMovieIdxsContainingTheEleId(helper:paramHelper, column_name:str, id:int, entire_df:pandas.DataFrame=entire_df_read) -> list:
    seriesAsLst = list(map(lambda x: eval(clean(x)), list(entire_df[column_name].fillna(r'[]'))))
    seriesAsIdsLst = list(map(lambda setsLst: [(int(s['id']) if 'id' in s else makeUpId(column_name, s)) for s in setsLst], seriesAsLst))
    ret_indices = [idx for (idx, ids) in enumerate(seriesAsIdsLst) if id in ids]
    return ret_indices

def rawHyperEdges(helper:paramHelper, column_names:list, entire_df:pandas.DataFrame=entire_df_read, n_edge_reserved=default_n_edge_reserved, print_start_end=False) -> list:
    if print_start_end:
        print('calculating rawHyperEdges: (all)', column_names)
    if type(column_names) != list:
        raise TypeError("param column_names should be a list of column names!")
    EdgesList = []
    for column_name in column_names:
        real_n_edge_reserved = default_n_edge_reserved
        seriesAsLst = list(map(lambda x: eval(clean(x)), list(entire_df[column_name].fillna(r'[]'))))
        chosen_ids = all_ids_and_frequency(column_name, train_df=entire_df, print_start_end=print_start_end)
        if len(chosen_ids) < n_edge_reserved:
            print(f'\tToo few items (total={len(chosen_ids)}) for n_edge={n_edge_reserved}. n_edge_reserved set to {len(chosen_ids)}.  (current column:"{column_name}")')
            real_n_edge_reserved = len(chosen_ids)
        chosen_ids = chosen_ids[:real_n_edge_reserved]
        H = torch.zeros((entire_df.shape[0], real_n_edge_reserved)).to(helper.device)
        for edgeIdx, tup in enumerate(chosen_ids):
            id = tup[0]
            H[allMovieIdxsContainingTheEleId(helper, column_name, id, entire_df), edgeIdx] = 1
        EdgesList.append(H)
    if print_start_end:
        print('finished rawHyperEdges: (all)', column_names)
    return EdgesList

def fineHyperEdges(helper: paramHelper, column_names:list, entire_df:pandas.DataFrame=entire_df_read, n_edge_reserved=default_n_edge_reserved, force_recompute=False, print_start_end=False) -> list:
    if print_start_end:
        print('calculating fineHyperEdges: (all)', column_names)
    if type(column_names) != list:
        raise TypeError("param column_names should be a list of column names!")
    ret = []
    for H in rawHyperEdges(helper, column_names=column_names, entire_df=entire_df, n_edge_reserved=n_edge_reserved, print_start_end=print_start_end):
        Hfine = H.T[(torch.sum(H, dim=0) >= 10) & (torch.sum(H, dim=0) <= 2000)].T
        ret.append(Hfine)
    if print_start_end:
        print('finished fineHyperEdges: (all)', column_names)
    return ret

HyperEdges = fineHyperEdges

def AdjMats(helper:paramHelper, column_names:list, force_recompute=False, n_edge_reserved=default_n_edge_reserved, entire_df=entire_df_read, print_start_end=False) -> list:
    if print_start_end:
        print('calculating AdjMats: (all)', column_names)
    if type(column_names) != list:
        raise TypeError("param column_names should be a list of column names!")
    fineHEs = fineHyperEdges(helper, column_names, n_edge_reserved=n_edge_reserved, force_recompute=force_recompute, entire_df=entire_df, print_start_end=print_start_end)
    ret_ = []
    for H in fineHEs:
        De = torch.diag(torch.sum(H, dim=0)).float()
        Deinv = torch.inverse(De)
        A = H @ Deinv @ H.T
        ret_.append(A)
    if print_start_end:
        print('finished AdjMats: (all)', column_names)
    return (ret_, fineHEs)

def fineGs(column_names:list, helper:paramHelper, batch_idx:int, force_recompute=False, n_edge_reserved=default_n_edge_reserved, print_start_end=False) -> list:
    if print_start_end:
        print('calculating fineGs: (all)', column_names)
    n_batch = helper.n_batch
    d = fineBatchInfo(helper, batch_idx)
    batchCombIdxs = d['batchCombIdxs']

    entire_df = entire_df_read.iloc[batchCombIdxs].copy()

    if type(column_names) != list:
        raise TypeError("param column_names should be a list of column names!")
    ret = []
    As_and_Hs = []
    z = []
    for i in range(len(column_names)):
        if os.path.exists('./fineGs/'+str(n_batch)+'/'+column_names[i]+str(n_edge_reserved)+'_btidx='+str(batch_idx)+'_G.pt') and not force_recompute:
            ret.append(torch.load('./fineGs/'+str(n_batch)+'/'+column_names[i]+str(n_edge_reserved)+'_btidx='+str(batch_idx)+'_G.pt').to(helper.device))
            if print_start_end:
                print('loaded: '+column_names[i]+str(n_edge_reserved)+'_btidx='+str(batch_idx)+'_G.pt')
        else:
            if As_and_Hs == []:
                As_and_Hs = AdjMats(helper, column_names, n_edge_reserved=n_edge_reserved, force_recompute=force_recompute, entire_df=entire_df, print_start_end=print_start_end)
                z = list(zip(As_and_Hs[0], As_and_Hs[1]))
            (A, H) = z[i]
            DV = torch.sum(H, dim=1).diag().float()
            DV2 = torch.pow(DV, -0.5)
            DV2 = torch.where(torch.isinf(DV2), 0., DV2)
            ret.append(DV2 @ A @ DV2)
            if not os.path.exists('./fineGs/'+str(n_batch)+'/'):
                os.makedirs('./fineGs/'+str(n_batch)+'/')
            torch.save(ret[-1], './fineGs/'+str(n_batch)+'/'+column_names[i]+str(n_edge_reserved)+'_btidx='+str(batch_idx)+'_G.pt')
    if print_start_end:
        print('finished fineGs: (all)', column_names)
    return ret

Gs = fineGs

if __name__ == "__main__":
    l = 'genres production_companies production_countries Keywords cast crew'.split()
    phtemp = paramHelper(n_batch=1)
    fineGs(l, phtemp, 0)

