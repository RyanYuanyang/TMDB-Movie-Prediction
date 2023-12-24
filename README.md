# TMDB-Movie-Prediction

FITE3010 group project

Name:
Chen Yuxuan 3035928455
Zhao jieyi
Fan Zheyu
Tu Yuanyang
He jiangchuan
Jonathan Cheung

## Project Description

This project is to predict the revenue of movies based on the data from TMDB. The dataset is from Kaggle. The dataset contains 3000+ movies with 23 features. The features include budget, genres, homepage, id, keywords, original_language, original_title, overview, popularity, production_companies, production_countries, release_date, revenue, runtime, spoken_languages, status, tagline, title, vote_average, vote_count, cast, crew. The target is to predict the revenue of movies.

## Data Preprocessing

### web crawler

since the train data is not enough, we try to get more data from the web. originally, there are 4000 training sample. After we remove all 0 revenue sample, we argument the training data to 7500 by merging them with the original data by unique imdb_id.

### Data Cleaning

since the data is dirty, we need to clean the data first. The data cleaning includes:

remove the data with:
revenue = 0
has mismatch column value and header

we fix the mojibake of column 'overview' and 'tagline', 'title' by using the function `fix_text` and store them in utf-8-sig format.

### Data analysis

### Feature Engineering

#### string feature to value

change the string feature ['genres', 'production_companies', 'production_countries', 'spoken_languages', 'cast', 'crew'] to value, like the number of genres, production_companies, production_countries, cast, crew.
and binary value
spoken_languages is English?, has homepage?,has tagline?, original_language is English?

#### word embedding

we use Bert to convert the string feature ['overview', 'tagline', 'title'] to vector. We use the pretrained model from huggingface. The final model we chose is 'all-mpnet-base-v2'. The output vector is 768 dimension.
we use both original vector and the vector after linear layer as the new feature.

feature dimension:
original vector: 768
vector after linear layer: 200, 1

##### developing process

we use BERT to generate contextualized word embeddings. This part embeds the sentences to vector space and do further analysis.

we have try many models to obtain the feature of string.
    1. all-mpnet-base-v2
    2. shibing624/text2vec-base-multilingual
    3. the other models from shibing624

and we finally decided to use the all-mpnet-base-v2 since it may perform better in this dataset.

we try to train the bert model by ourself. But the result is not good since the loss is keeping increasing. This can be caused by the training method.

Since we want to concentrate the information separately and merge them together by linear layer, we also try to embedding tagline, title, overview separately, and pass them to the linear layer and add together to predict the revenue, but the result is not good.

TA provided some ideas, he said we can add the tagline, title, overview together.

at the same time, we want to output the feature vector rather than just a single value, I add a function in the self-define 3 full connection layer that will output the 200-d vector after doing 2 full connection process.

How to measure the performance?
process:
    1. embedding the text
    2. build a 3 layer full connection regressor
    3. randomly split the data with a 8:2 train test ratio.
    4. train full connection layer with the data
    5. calculate the RMSE and correlation coefficient between the predicted revenue with the test revenue.
    6. draw the TSNE graph to see the distribution of 200-d vector

## Model Selection

### 1
Linear Regression Model

score: 2.0167

### 2
Random Forest Model

score: 2.22765

### 3
Error Detection Model

use lightgbm as the error identifer and use lightgbm, xgboost, catboost as the regressor. The error identifier will identify the error data and non-error data. And there will be two regressor. One regressor will train on the error data and the other regressor will train on the non-error data. The final result will be the sum of the two regressor.

score: 2.16366


### 4
Aggregation Model

use a linear combination of the result of the three model above to achieve the final result.

score: 1.96185


### 5
HGNN
Hypergraph Neuron Network

score: 2.38254

## Result

"submission_aggregate.csv"

score: 1.96185

## Conclusion
