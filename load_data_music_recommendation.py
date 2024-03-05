import numpy as np 
import pandas as pd 
import warnings 
warnings.filterwarnings("ignore")
from matplotlib import pyplot as plt 
import seaborn as sns
import lightfm 
from lightfm import LightFM, cross_validation
from lightfm.evaluation import auc_score  
from scipy import sparse


df_artist = pd.read_csv('https://raw.githubusercontent.com/Gurobi/modeling-examples/master/music_recommendation/artist_data.csv')
df_playlist = pd.read_csv('https://raw.githubusercontent.com/Gurobi/modeling-examples/master/music_recommendation/user_playlist_data.csv')


def load_model():
    df_freq = df_playlist.groupby(['user_id', 'artist']).agg('size').reset_index().rename(columns={0:'freq'})[['user_id', 'artist', 'freq']].sort_values(['freq'], ascending=False)
    df_freq = df_freq.merge(df_artist[['artist_id','artist']], left_on='artist', right_on='artist') 

    # Input matrix 
    input_matrix = df_freq.groupby(['user_id', 'artist_id'])['freq'].sum().unstack().reset_index().fillna(0).set_index('user_id')

    # Dictionary to track the artist id for each artist name
    artists_dict ={(df_artist.loc[i,'artist_id']): df_artist.loc[i,'artist'] for i in range(df_artist.shape[0])} 
    x = sparse.csr_matrix(input_matrix.values)  
    train, test = lightfm.cross_validation.random_train_test_split(x, test_percentage=0.2, random_state=None)

    ### Train the Matrix Factorization Model  
    model = LightFM(no_components=50, loss='warp')
    model.fit(x, epochs=30, num_threads = 4)
    
    train_auc = auc_score(model, train, num_threads=4).mean()  
    test_auc = auc_score(model, test, train_interactions=train, num_threads=4).mean()

    return model, input_matrix, artists_dict, df_artist, df_playlist