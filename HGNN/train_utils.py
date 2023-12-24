import torch
import pandas as pd
import pandas
import time
import os
from models.paramHelper import paramHelper

entire_df_read = pd.read_csv('entire.csv', encoding='utf-8-sig')

def embedding_ver1(paramHelper, entire_df:pandas.DataFrame=entire_df_read) -> torch.Tensor:
    """
    embedding: 19-dim tensor
    """
    format_tar = ['budget', 'true_budget', 'popularity', 'runtime', 'cast_num', 'crew_num',
       'keyword_num', 'spoken_languages_num', 'production_countries_num',
       'production_companies_num', 'genres_num', 'belongs_to_collection_num',
       'ReleaseYear', 'ReleaseMonth', 'ReleaseDay', 'hasHomepage',
       'hasTagline', 'changedTitle', 'originalLanguageEng']
    raw = torch.from_numpy(entire_df[format_tar].to_numpy()).float().to(paramHelper.device)
    return raw

def preProcess(paramHelper) -> tuple:
    '''
    return (tensor(shape: 9354, 19), tensor(shape: 9354, ))'''
    raw_revenues = torch.from_numpy(entire_df_read.revenue.to_numpy()).float().to(paramHelper.device)
    labels_fullpass = torch.where(raw_revenues != -1, torch.log1p(raw_revenues), -1).to(paramHelper.device)

    raw_datas = embedding_ver1(paramHelper=paramHelper, entire_df=entire_df_read)
    raw_datas[:, 0] = torch.log1p(raw_datas[:, 0])
    raw_datas[:, 1] = torch.log1p(raw_datas[:, 1])

    datas_fullpass = raw_datas
    mean, std = torch.mean(datas_fullpass[:, 1:], dim=0), torch.std(datas_fullpass[:, 1:], dim=0)
    datas_fullpass[:, 1:] = (datas_fullpass[:, 1:] - mean) / std

    mean0, std0 = torch.mean(datas_fullpass[:, 0], dim=0), torch.std(datas_fullpass[:, 0], dim=0)
    datas_fullpass[:, 1:] = (datas_fullpass[:, 1:] * std0) + mean0

    return (datas_fullpass, labels_fullpass)

def fineBatchInfo(paramHelper, batch_idx) -> dict:
    d, l = preProcess(paramHelper=paramHelper)
    tr = paramHelper.trainOnlyIdxses[batch_idx]
    te = paramHelper.testOnlyIdxses[batch_idx]
    cb = paramHelper.batchCombIdxses[batch_idx]
    return {'allDataFullPass':d, 'allLabelFullPass':l, 'trainOnlyIdxs':tr, 'testOnlyIdxs':te, 'batchCombIdxs':cb}


if __name__ == "__main__":
    p = paramHelper()
    f = fineBatchInfo(p, 0)
