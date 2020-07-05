# This is the script for the Module 8 Challenge Assignment.

# Objectives:

# 1) Create a function that takes in three arguments: Wikipedia data, Kaggle data, and MovieLens (Kaggle) review data
# 2) Use the code from your Jupyter Notebook so that the function performs all of the transformation steps. Remove any exploratory data analysis and redundant code.
# 3) Add the load steps from the Jupyter Notebook to the function. You’ll need to remove the existing data from SQL, but keep the empty tables.
# 4) Check that the function works correctly on the current Wikipedia and Kaggle data.
# 5) Document any assumptions that are being made. Use try-except blocks to account for unforeseen problems that may arise with new data.

# -------------------------------------

# Import Dependencies:
import json
import pandas as pd
import numpy as np 
import time
from sqlalchemy import create_engine
from config import db_password 

# Define File Paths

wiki_file = '/Users/sathvik/Desktop/Data Analytics Boot Camp/Analytics Projects/Movies Analysis/Resources/wikipedia.movies.json'
kaggle_file = '/Users/sathvik/Desktop/Data Analytics Boot Camp/Analytics Projects/Movies Analysis/Resources/movies_metadata.csv'
ratings_file = '/Users/sathvik/Desktop/Data Analytics Boot Camp/Analytics Projects/Movies Analysis/Resources/ratings.csv'

# Function:

def extract_transform_load(wiki_file, kaggle_file, ratings_file):
    ## STEP 1: EXTRACT

    ### Extract wikipedia, kaggle, and MovieLens data:
    with open(f'{wiki_file}', mode='r') as file:
        wiki_movies_raw = json.load(file)
    
    ######## COME BACK TO THIS: wiki_movies_df = pd.DataFrame(wiki_movies_raw)

    kaggle_metadata = pd.read_csv(f'{kaggle_file}',low_memory=False)
    
    ratings = pd.read_csv(f'{ratings_file}')
    
    ## STEP 2: TRANSFORM

    ### Start with the Wikipedia data (starts with 193 columns)

    #### Assumption 1: We should filter to movies that contain both an IMDB link and a listed director:
    wiki_movies = [movie for movie in wiki_movies_raw
               if ('Director' in movie or 'Directed by' in movie)
                   and 'imdb_link' in movie]
    
    ##### Put this shortened list into a dataframe (now has only 78 columns)
    wiki_movies_df = pd.DataFrame(wiki_movies)

    #### Assumption 2: Listings with greater than one episode are TV shows, not movies, and should be removed


    ## STEP 3: LOAD

    ### Import Dependencies to create a database engine and define the database string:
    from sqlalchemy import create_engine
    from config import db_password
    import time

    db_string = f"postgres://postgres:{db_password}@127.0.0.1:5432/Challenge8_movie_data"

    ### Create database engine:
    engine = create_engine(db_string)

    ### Import movie data:
    movies_with_ratings_df.to_sql(name='Challenge8_Movies', con=engine) ###CHECK IF THIS IS MWR_DF or just movies_Df

    ### Import ratings data:
    rows_imported = 0

    start_time = time.time()

    for data in pd.read_csv(f'{ratings_file}', chunksize=1000000):
        print(f'importing rows {rows_imported} to {rows_imported + len(data)}...', end='')
        data.to_sql(name='ratings', con=engine, if_exists='append')
        rows_imported += len(data)

    print(f'Done. {time.time() - start_time} total seconds elapsed')

