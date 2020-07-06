# This is the script for the Module 8 Challenge Assignment.

# Objectives:

# 1) Create a function that takes in three arguments: Wikipedia data, Kaggle data, and MovieLens (Kaggle) review data
# 2) Use the code from your Jupyter Notebook so that the function performs all of the transformation steps. Remove any exploratory data analysis and redundant code.
# 3) Add the load steps from the Jupyter Notebook to the function. You’ll need to remove the existing data from SQL, but keep the empty tables.
# 4) Check that the function works correctly on the current Wikipedia and Kaggle data.
# 5) Document any assumptions that are being made. Use try-except blocks to account for unforeseen problems that may arise with new data.

# -------------------------------------


# Function:

def extract_transform_load(wiki_file, kaggle_file, ratings_file):
    # Import Dependencies:
    import json
    import pandas as pd
    import numpy as np

    
    ## STEP 1: EXTRACT

    ### Extract wikipedia, kaggle, and MovieLens data:
    with open(f'{wiki_file}', mode='r') as file:
        wiki_movies_raw = json.load(file)
    
    kaggle_metadata = pd.read_csv(f'{kaggle_file}',low_memory=False)
    
    ratings = pd.read_csv(f'{ratings_file}')
    
    ## This ends the EXTRACT section!

  
    ## STEP 2: TRANSFORM

    ### Start with the Wikipedia data (starts with 193 columns)

    #### Assumption 1: We should filter to movies that contain both an IMDB link and a listed director.
    #### Assumption 2: We should remove listings with "No. of Episodes", as these likely refer to TV shows.
    
    wiki_movies = [movie for movie in wiki_movies_raw
               if ('Director' in movie or 'Directed by' in movie)
                   and 'imdb_link' in movie
                   and 'No. of episodes' not in movie]
    

    #### Assumption 3: Alternate titles can be combined into one list to reduce the number of columns without losing data

    ### Use a lambda function to clean Wikipedia data:
    def clean_movie(movie):
        movie = dict(movie) #create a non-destructive copy
        alt_titles = {}

        #### Combine alternate titles into one list
        for key in ['Also known as','Arabic','Cantonese','Chinese','French',
                    'Hangul','Hebrew','Hepburn','Japanese','Literally',
                    'Mandarin','McCune-Reischauer','Original title','Polish',
                    'Revised Romanization','Romanized','Russian',
                '   Simplified','Traditional','Yiddish']:
            if key in movie:
                alt_titles[key] = movie[key]
                movie.pop(key)
        if len(alt_titles) > 0:
            movie['alt_titles'] = alt_titles

        #### Merge column names
        def change_column_name(old_name, new_name):
            if old_name in movie:
                movie[new_name] = movie.pop(old_name)
    
        change_column_name('Adaptation by', 'Writer(s)')
        change_column_name('Country of origin', 'Country')
        change_column_name('Directed by', 'Director')
        change_column_name('Distributed by', 'Distributor')
        change_column_name('Edited by', 'Editor(s)')
        change_column_name('Length', 'Running time')
        change_column_name('Original release', 'Release date')
        change_column_name('Music by', 'Composer(s)')
        change_column_name('Produced by', 'Producer(s)')
        change_column_name('Producer', 'Producer(s)')
        change_column_name('Productioncompanies ', 'Production company(s)')
        change_column_name('Productioncompany ', 'Production company(s)')
        change_column_name('Released', 'Release Date')
        change_column_name('Release Date', 'Release date')
        change_column_name('Screen story by', 'Writer(s)')
        change_column_name('Screenplay by', 'Writer(s)')
        change_column_name('Story by', 'Writer(s)')
        change_column_name('Theme music composer', 'Composer(s)')
        change_column_name('Written by', 'Writer(s)')

        return movie


    ### Run the lambda function and update the dataframe:
    clean_movies = [clean_movie(movie) for movie in wiki_movies]
    wiki_movies_df = pd.DataFrame(clean_movies)

    #### Assumption 4: There are likely duplicate entries for some of the movies.
    wiki_movies_df['imdb_id'] = wiki_movies_df['imdb_link'].str.extract(r'(tt\d{7})')
    wiki_movies_df.drop_duplicates(subset='imdb_id', inplace=True)

    #### Assumption 5: There are likely many columns with null data
    wiki_columns_to_keep = [column for column in wiki_movies_df.columns if wiki_movies_df[column].isnull().sum() < len(wiki_movies_df) * 0.9]
    wiki_movies_df = wiki_movies_df[wiki_columns_to_keep]

    #### Assumption 6: Some columns may have data represented in different ways, such as the budget column (Ex: $123.4M vs. $123.4 Million vs. $123,400,000 vs. $123400000)
    ##### Changes to be made: budget --> numeric; box office --> numeric; release date --> datetime; run time --> numeric

    import re 

    #### Box Office -- change to numeric: 
    ##### Assumption 6.1: There are two main forms of numeric formats for box office and budget values

    box_office = wiki_movies_df['Box office'].dropna() 

    lambda x: type(x) != str

    box_office[box_office.map(lambda x: type(x) != str)]

    box_office = box_office.apply(lambda x: ' '.join(x) if type(x) == list else x)

    form_one = r'\$\s*\d+\.?\d*\s*[mb]illi?on'
    form_two = r'\$\s*\d{1,3}(?:[,\.]\d{3})+(?!\s[mb]illion)'

    ##### Parse box office values
    def parse_dollars(s):
        # if s is not a string, return NaN
        if type(s) != str:
            return np.nan

        # if input is of the form $###.# million
        if re.match(r'\$\s*\d+\.?\d*\s*milli?on', s, flags=re.IGNORECASE):

            # remove dollar sign and " million"
            s = re.sub('\$|\s|[a-zA-Z]','', s)

            # convert to float and multiply by a million
            value = float(s) * 10**6

            return value

        # if input is of the form $###.# billion
        elif re.match(r'\$\s*\d+\.?\d*\s*billi?on', s, flags=re.IGNORECASE):

            # remove dollar sign and " billion"
            s = re.sub('\$|\s|[a-zA-Z]','', s)

            # convert to float and multiply by a billion
            value = float(s) * 10**9

            return value

        # if input is of the form $###,###,###
        elif re.match(r'\$\s*\d{1,3}(?:[,\.]\d{3})+(?!\s[mb]illion)', s, flags=re.IGNORECASE):

            # remove dollar sign and commas
            s = re.sub('\$|,','', s)

            # convert to float
            value = float(s)
            return value

        # otherwise, return NaN
        else:
            return np.nan

    wiki_movies_df['box_office'] = box_office.str.extract(f'({form_one}|{form_two})', flags=re.IGNORECASE)[0].apply(parse_dollars)

    wiki_movies_df.drop('Box office', axis=1, inplace=True)    

    
    #### Budget -- change to numeric: 
    budget = wiki_movies_df['Budget'].dropna()
    
    budget = budget.map(lambda x: ' '.join(x) if type(x) == list else x)

    budget = budget.str.replace(r'\$.*[-—–](?![a-z])', '$', regex=True)

    budget = budget.str.replace(r'\[\d+\]\s*', '')

    ##### Parse budget values:
    wiki_movies_df['budget'] = budget.str.extract(f'({form_one}|{form_two})', flags=re.IGNORECASE)[0].apply(parse_dollars)

    wiki_movies_df.drop('Budget', axis=1, inplace=True)


    #### Release Date -- change to datetime:
    release_date = wiki_movies_df['Release date'].dropna().apply(lambda x: ' '.join(x) if type(x) == list else x)

    ##### Assumption 6.2: There are 4 main forms of dates. 
        # Full month name, one- to two-digit day, four-digit year (i.e., January 1, 2000)
        # Four-digit year, two-digit month, two-digit day, with any separator (i.e., 2000-01-01)
        # Full month name, four-digit year (i.e., January 2000)
        # Four-digit year

    date_form_one = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s[123]\d,\s\d{4}'
    date_form_two = r'\d{4}.[01]\d.[123]\d'
    date_form_three = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}'
    date_form_four = r'\d{4}'

    wiki_movies_df['release_date'] = pd.to_datetime(release_date.str.extract(f'({date_form_one}|{date_form_two}|{date_form_three}|{date_form_four})')[0], infer_datetime_format=True)

    #### Running Time -- change to numeric:
    running_time = wiki_movies_df['Running time'].dropna().apply(lambda x: ' '.join(x) if type(x) == list else x)

    running_time_extract = running_time.str.extract(r'(\d+)\s*ho?u?r?s?\s*(\d*)|(\d+)\s*m')

    ##### Convert lists to strings -- fill empty cells with 0
    running_time_extract = running_time_extract.apply(lambda col: pd.to_numeric(col, errors='coerce')).fillna(0)

    wiki_movies_df['running_time'] = running_time_extract.apply(lambda row: row[0]*60 + row[1] if row[2] == 0 else row[2], axis=1)

    wiki_movies_df.drop('Running time', axis=1, inplace=True)

    ### Marks the end of cleaning up the Wikipedia data!


    ### Transform Kaggle Metadata:
    
    #### Clean up Adult column:
    kaggle_metadata = kaggle_metadata[kaggle_metadata['adult'] == 'False'].drop('adult',axis='columns')

    #### Clean up Video column:
    kaggle_metadata['video'] = kaggle_metadata['video'] == 'True'

    #### Convert numeric columns:
    kaggle_metadata['budget'] = kaggle_metadata['budget'].astype(int)
    kaggle_metadata['id'] = pd.to_numeric(kaggle_metadata['id'], errors='raise')
    kaggle_metadata['popularity'] = pd.to_numeric(kaggle_metadata['popularity'], errors='raise')

    #### Convert Release Date to datetime:
    kaggle_metadata['release_date'] = pd.to_datetime(kaggle_metadata['release_date'])

    ### Transform the Kaggle Ratings Data:

    #### Convert Timestamp to datetime:
    ratings['timestamp'] = pd.to_datetime(ratings['timestamp'], unit='s')


    ### Merge Wikipedia and Kaggle Metadata into movies_df:

    #### Assumption 7: There is some redundant data between our different datasets. We will decide to keep some while dropping others, as follows:
        # Competing data:
        # Wiki                     Movielens                Resolution
        #--------------------------------------------------------------------------
        # title_wiki               title_kaggle             Drop Wikipedia -- kaggle is better, and no missing values
        # running_time             runtime                  Keep Kaggle; fill in zeros with Wikipedia data.
        # budget_wiki              budget_kaggle            Keep Kaggle; fill in zeros with Wikipedia data.
        # box_office               revenue                  Keep Kaggle; fill in zeros with Wikipedia data.
        # release_date_wiki        release_date_kaggle      Drop Wikipedia -- kaggle is better, and no missing values
        # Language                 original_language        Drop Wikipedia to avoid hassle
        # Production company(s)    production_companies     Drop Wikipedia, kaggle is more consistent


    #### Inner join metadata and wikipedia after cleaning:
    movies_df = pd.merge(wiki_movies_df, kaggle_metadata, on='imdb_id', suffixes=['_wiki','_kaggle'])

    ratings['timestamp'] = pd.to_datetime(ratings['timestamp'], unit='s') # remove outlier
    movies_df['Language'].apply(lambda x: tuple(x) if type(x) == list else x).value_counts(dropna=False) # convert languages to tuple

    movies_df.drop(columns=['title_wiki','release_date_wiki','Language','Production company(s)'], inplace=True)

    ##### Create a function to fill in missing data:
    def fill_missing_kaggle_data(df, kaggle_column, wiki_column):
        df[kaggle_column] = df.apply(
            lambda row: row[wiki_column] if row[kaggle_column] == 0 else row[kaggle_column]
            , axis=1)
        df.drop(columns=wiki_column, inplace=True)

    ##### Run the function on runtime, budget, and revenue pairs:
    fill_missing_kaggle_data(movies_df, 'runtime', 'running_time')
    fill_missing_kaggle_data(movies_df, 'budget_kaggle', 'budget_wiki')
    fill_missing_kaggle_data(movies_df, 'revenue', 'box_office')

    ##### Reorder Columns:
    movies_df = movies_df.loc[:, ['imdb_id','id','title_kaggle','original_title','tagline','belongs_to_collection','url','imdb_link',
                       'runtime','budget_kaggle','revenue','release_date_kaggle','popularity','vote_average','vote_count',
                       'genres','original_language','overview','spoken_languages','Country',
                       'production_companies','production_countries','Distributor',
                       'Producer(s)','Director','Starring','Cinematography','Editor(s)','Writer(s)','Composer(s)','Based on'
                      ]]

    ##### Rename Columns:
    movies_df.rename({'id':'kaggle_id',
                  'title_kaggle':'title',
                  'url':'wikipedia_url',
                  'budget_kaggle':'budget',
                  'release_date_kaggle':'release_date',
                  'Country':'country',
                  'Distributor':'distributor',
                  'Producer(s)':'producers',
                  'Director':'director',
                  'Starring':'starring',
                  'Cinematography':'cinematography',
                  'Editor(s)':'editors',
                  'Writer(s)':'writers',
                  'Composer(s)':'composers',
                  'Based on':'based_on'
                 }, axis='columns', inplace=True)

    #### Merge movies_df and ratings data:

    rating_counts = ratings.groupby(['movieId','rating'], as_index=False).count() \
                .rename({'userId':'count'}, axis=1) \
                .pivot(index='movieId',columns='rating', values='count')

    rating_counts.columns = ['rating_' + str(col) for col in rating_counts.columns]

    ##### Left Merge:
    movies_with_ratings_df = pd.merge(movies_df, rating_counts, left_on='kaggle_id', right_index=True, how='left')

    ##### Fill NA with 0s:
    movies_with_ratings_df[rating_counts.columns] = movies_with_ratings_df[rating_counts.columns].fillna(0)

    ## This ends the TRANSFORM section!


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

    ## This ends the LOAD section!

# -------------------------------------

# This section is not part of the function

# Define File Paths
wiki_file = '/Users/sathvik/Desktop/Data Analytics Boot Camp/Analytics Projects/Movies Analysis/Resources/wikipedia.movies.json'
kaggle_file = '/Users/sathvik/Desktop/Data Analytics Boot Camp/Analytics Projects/Movies Analysis/Resources/movies_metadata.csv'
ratings_file = '/Users/sathvik/Desktop/Data Analytics Boot Camp/Analytics Projects/Movies Analysis/Resources/ratings.csv'

# Run the function
extract_transform_load(wiki_file,kaggle_file,ratings_file)