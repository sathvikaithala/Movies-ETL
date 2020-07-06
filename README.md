# Movies - Extract, Transform, and Load

UC Berkeley Extension Data Analytics Boot Camp Module 8
---

## Overview

In this module, we performed the Extract, Transform, and Load (ETL) process on three data sources to generate an SQL database of movies. The movie information and links came from Wikipedia articles (in a JSON format) and the review information came from Kaggle (in CSV format). 

Once we had imported the data into various Pandas DataFrames, we cleaned up the data to remove extraneous columns, merge various formats, and convert data types where needed.

We then loaded the data into a SQL database. 

We were then tasked with creating a Python function that takes in three input files and performs the ETL process. This file is saved as "challenge.py". In doing this, we were asked to document our assumptions for transformations we performed to clean up the data.

*Note: The file titled "Movies_Challenge-TEST" was created to run the function in a Jupyter Notebook to check and make sure everything functioned as desired.*

---

## Assumptions

### The following assumptions were made in our analysis:

1) <b>We should filter to movies that contain both an IMDB link and a listed director.</b> This reduces the number of data points we have without IMDB data we can use to link our multiple data sources.

2) <b>We should remove listings with "No. of Episodes".</b> We assume that these entries refer to television shows. While there are not many data points that had this issue, it allowed us to clean up data that is obviously not related to a movie.

3) <b>Alternate titles can be combined into one list.</b>  This reduces the number of columns without losing information related to the movie.

4) <b>There are likely duplicate entries for some of the movies.</b> Given the size of our source data, it is not unreasonable to assume that some movies might be duplicated. Removing these duplicates allows us to pare down the size of our dataset, while simultaneously giving us more valuable information to work with.

5) <b>There are likely many columns with null data.</b> Since some entries may have null values for many of the columns due to the quality of data uploaded by contributers, we determined that we would check for columns that were *mostly* (>90%) empty and remove them from our dataset.

6) <b>Some columns may have data represented in different formats</b> We used REGEX functions to clean up these inconsistencies. Some examples are listed below:

  6a) <b>There are two main forms of numeric formats for box office and budget values.</b> Ex: $123.4 Million vs. $123,400,000. However, within these two formats, there are many potential variations. 
  
  6b) <b>There are 4 main forms of dates.</b> They are as follows:
        - Full month name, one- to two-digit day, four-digit year (i.e., January 1, 2000)
        - Four-digit year, two-digit month, two-digit day, with any separator (i.e., 2000-01-01)
        - Full month name, four-digit year (i.e., January 2000)
        - Four-digit year
  
7) <b>There is some redundant data between our different datasets.</b> We will decide to keep some while dropping others, as follows:
        
         Wiki                     Movielens                Resolution
        --------------------------------------------------------------------------
         title_wiki               title_kaggle             Drop Wikipedia -- Kaggle is better, and no missing values
         running_time             runtime                  Keep Kaggle; fill in zeros with Wikipedia data.
         budget_wiki              budget_kaggle            Keep Kaggle; fill in zeros with Wikipedia data.
         box_office               revenue                  Keep Kaggle; fill in zeros with Wikipedia data.
         release_date_wiki        release_date_kaggle      Drop Wikipedia -- Kaggle is better, and has no missing values
         Language                 original_language        Drop Wikipedia to avoid hassle
         Production company(s)    production_companies     Drop Wikipedia, Kaggle is more consistent

---


