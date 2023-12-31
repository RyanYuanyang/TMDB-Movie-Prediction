# TMDB-Movie-Prediction

FITE3010 group project

Name:  

Chen Yuxuan 3035928455

Zhao jieyi 3035844390

Fan Zheyu 3035845203

Tu Yuanyang 3035832476

He jiangchuan 3035771945

Cheung Yau Shing Jonathan 3035783560  

## Environment

Python 3.8.16

**data analysis**:

- pandas, numpy, matplotlib, seaborn, wordcloud, scipy
  
**model**:

- sklearn, lightgbm, xgboost, catboost, text2vec, transformer,pytorch
  
**other lib**:

- tqdm

## Running order

1. DataAnalysis.ipynb
2. FeatureEngineering.ipynb
3. Models
    - Model.ipynb
    - sentence_embedding.ipynb
    - HGNN

## Project Description

This project aims to predict movie revenue based on data from TMDB. The dataset is from Kaggle. The dataset contains 3000+ movies with 23 features. The features include budget, genres, homepage, id, keywords, original_language, original_title, overview, popularity, production_companies, production_countries, release_date, revenue, runtime, spoken_languages, status, tagline, title, vote_average, vote_count, cast, crew. The target is to predict the revenue of movies.

## Data Preprocessing

### web crawler

Since the train data is not enough, we try to get more data from the web. Initially, there were 4000 training samples. After we remove all 0 revenue samples, we augment the training data to 7500 by merging them with the original data by unique imdb_id.

### Data Cleaning

Since the data is dirty, we need to clean it first. The data cleaning includes:

Remove the data with:
revenue = 0
has a mismatch in column value and header

We fix the mojibake of columns 'overview' and, 'tagline,' 'title' by using the function `fix_text` and storing them in utf-8-sig format.

### Data analysis

There is a lot of unfilled data in training and testing; keywords and the homepage are the most unfilled.
We try to measure the distribution of missing features and the correlation to see if they can be used to be a feature.

<!-- we try to visualize the target prediction value, which is revenue. And we find that the revenue distribution under log1p is more like a normal distribution.

At the same time, we found that there are many outliers and errors, like revenue = 1

we find that the revenue is highly correlated with budget, but there are many movies with 0 budget.

we try to find the frequency of each category in the genres and find that the most common genres is drama, comedy, Drama Romance.

we find that there are many movies with no homepage.
Most of hte movies use English as their original language, and seems that English -->

### Feature Engineering

After we analyze the data, we do some feature engineering to the data and use them to train our model.

The process of feature engineering includes the following:
string feature -> numerical feature
string feature -> binary feature
string feature -> word embedding
year, week, which day of the week -> numerical feature

#### string feature to value

Change the string feature ['genres', 'production_companies', 'production_countries', 'spoken_languages', 'cast', 'crew'] to value, like the number of genres, production_companies, production_countries, cast, crew.
and binary value
spoken_languages is English?, has homepage?,has tagline?, original_language is English?

#### word embedding

We used Bert to convert the string feature ['overview,' 'tagline,' 'title'] to vector. We use the pre-trained model from hugging face. The final model we chose is 'all-mpnet-base-v2'. The output vector is 768 dimensions.
We use both the original vector and the vector after the linear layer as the new feature.

The method to embed the features together is to add them up and pass them to the Bert model.

Feature dimension:
original vector: 768
vector after linear layer: 200, 1

## Model Selection

### 1

Linear Regression Model
The model is not quite stable, results varies from 2.099 to 2.017.

score: 2.0652

### 2

Random Forest Model
The model is tuned with different parameters, n_etimaters (50 - 1000), min_samples_split (2 - 100), max_depth (10 - 200).

score: 2.14405

### 3

Error Detection Model

use lightgbm as the error identifer and use lightgbm, xgboost, catboost as the regressor. The error identifier will identify the error data and non-error data. And there will be two regressor. One regressor will train on the error data and the other regressor will train on the non-error data. The final result will be the sum of the two regressor.

score: 2.07727

### 4

Aggregation Model

use a linear combination of the result of the three model above to achieve the final result.

score: 1.92684

### 5

Hypergraph Neuron Network  
Used a 6-channel HGNN, utilizing the "json-formatted" columns (which is ignored by most of the other groups and most of the public notebooks on kaggle website) of the data to mine the possible latent "relationship/closeness" of movies.

score: 2.38254

### 6

Bert

Only use tagline + overview + title as the feature. After passing the BERT model, we use linear regression to predict the revenue.

score: 2.81

Running method:
download the model from huggingface: website: <https://huggingface.co/sentence-transformers/all-mpnet-base-v2>
and put the model in the folder: TMDB-Movie-Prediction\sentence_embedding\
the full path is: TMDB-Movie-Prediction\sentence_embedding\all-mpnet-base-v2

Then run the sentence_embedding.ipynb. The output features and prediction result will be in the folder: TMDB-Movie-Prediction\sentence_embedding\

The file 'one_dim_feature_test.csv' is the model's output result, and the original_pred column is the predicted revenue.

Test result: this feature will cause overfitting; should not use it

## Result

"submission_aggregate.csv"

score: 1.92684

## Conclusion

The given data is very complicated, and there is a lot of missing data. We try to use different method to separate the feature from the data and use them to train the model. Above are the results of the model we tested.

Since Bert only uses the string as the feature and does not use any numerical and categorical feature, the result is not good.We have also tried the Bert model and outputted the feature, but the result is also not good. we think that it is because the large dimension of the feature causes the model to overfit. At the same time, we have also tried to use the single dimension feature (log revenue); the model we train always gives a large weight to it, which causes the result to have a large error.

HGNN will use the JSON feature, and the result is better than Bert's, but the result is not good enough.

Since we find that the catboost, xgboost, lightgbm model output similar result (around 2.1), combining them together will get a better result. And the result is better than the single model.

Finally, we decided to use the aggregation model as our final model and combine them by linear combination.
