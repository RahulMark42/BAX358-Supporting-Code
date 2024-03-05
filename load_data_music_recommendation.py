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



def vis_data():
    df_artist.set_index('artist')['listeners'].head(2000).plot(kind='line', figsize=(6, 4), color='skyblue', rot=40)
    plt.xlabel('Number of listeners (millions)')
    plt.ylabel('Artist')
    plt.title('Listeners for Top 2000 Artists') 
    plt.show()

    df_country = df_artist.groupby('country')['country'].count().sort_values(ascending = False).reset_index(name="count")
    df_country.set_index('country')['count'].plot(kind='line', figsize=(6, 4), color='skyblue', rot=40) 
    plt.xlabel('Country')
    plt.ylabel('Number of artists originating from the country') 
    plt.show() 


def model():
    # Dataframe that stores the frequency of artists as they appear in users' playlists
    df_freq = df_playlist.groupby(['user_id', 'artist']).agg('size').reset_index().rename(columns={0:'freq'})[['user_id', 'artist', 'freq']].sort_values(['freq'], ascending=False)
    df_freq = df_freq.merge(df_artist[['artist_id','artist']], left_on='artist', right_on='artist') 

    # Input matrix 
    input_matrix = df_freq.groupby(['user_id', 'artist_id'])['freq'].sum().unstack().reset_index().fillna(0).set_index('user_id')

    # Dictionary to track the artist id for each artist name
    artists_dict ={(df_artist.loc[i,'artist_id']): df_artist.loc[i,'artist'] for i in range(df_artist.shape[0])} 
    ### Train-Test split
    x = sparse.csr_matrix(input_matrix.values)  
    train, test = lightfm.cross_validation.random_train_test_split(x, test_percentage=0.2, random_state=None)

    ### Train the Matrix Factorization Model  
    model = LightFM(no_components=50, loss='warp')
    model.fit(x, epochs=30, num_threads = 4)
    
    train_auc = auc_score(model, train, num_threads=4).mean()  
    test_auc = auc_score(model, test, train_interactions=train, num_threads=4).mean()
    print('Train AUC: %f, test AUC: %f'%(train_auc,test_auc))

    global preference, df_pref
    preference = pd.Series(model.predict(x, np.arange(input_matrix.shape[1]))).to_dict()
    lower_score = min(preference.values())
    highest_score = max(preference.values())
    preference = {artists_dict[i]:(preference[i]-lower_score)/(highest_score-lower_score) for i in preference}  
     
    # Print the known likes of the user
    known_items = list(pd.Series(input_matrix.loc[x,:][input_matrix.loc[x,:] > 0].index).sort_values(ascending=False))
    known_items = list(pd.Series(known_items).apply(lambda x: artists_dict[x])) 
    print("Top 20 artists this user already likes:\n",known_items[:20]) 
     
    # Print the predicted preference scores of the user
    df_pref = pd.DataFrame.from_records([(k, v) for k, v in preference.items()], columns =['artist', 'preference']) 
    df_pref = df_artist.merge(df_pref,left_on='artist',right_on='artist').sort_values(by = 'preference',ascending=False)

    artists = sorted(preference.keys(),reverse=True,key=lambda x : preference[x])[:1000]  # Set of the most preferred 1000 artists
    popularity = df_artist.groupby('artist')['listeners'].apply(float).to_dict() # Popularity of each artist

    return artists, popularity