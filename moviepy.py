# -*- coding: utf-8 -*-
"""Untitled6.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1rdD9b73hsvvUQdY1eM_rywFU8fIxUCxq
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ipywidgets import *

# Load data
movies = pd.read_csv('movies.csv')
ratings = pd.read_csv('ratings.csv')

# Display data types
print(movies.dtypes)

# Display the first few rows
print(movies.head())
print(ratings.head())

# Check for null values
movies.info()
ratings.info()

# Preprocess genres
movies['genres'] = movies['genres'].str.split("|")
movies = movies.explode('genres')
movies = movies.replace('', np.nan)
movies = movies[movies['genres'] != '(no genres listed)']

# Merge ratings and movies data
merged_data = pd.merge(ratings, movies, on='movieId', how='inner')

# Popularity based recommendation system
def TopNPopularMovies(genre, threshold, topN):
    popularity = merged_data.groupby(['genres', 'title']).agg({'rating': ['mean', 'size']}).reset_index()
    popularity.columns = ["Genres", "Title", "Average Ratings", "Number of Ratings"]
    topNrecommendations = popularity[(popularity['Genres'] == genre) & (popularity['Number of Ratings'] >= threshold)]
    topNrecommendations = topNrecommendations.sort_values(by='Average Ratings', ascending=False).head(topN)
    topNrecommendations['Sno.'] = range(1, len(topNrecommendations) + 1)
    topNrecommendations.index = range(0, len(topNrecommendations))
    topNrecommendations.columns = ['Genres', 'Movie Title', 'Average Movie Rating', 'Number of Reviews', 'Sno.']
    return topNrecommendations[['Sno.', 'Movie Title', 'Average Movie Rating', 'Number of Reviews']]

# Content based recommendation system
movies3 = movies.groupby('title').agg({"genres": lambda x: " ".join(list(x))}).reset_index()
tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), stop_words='english')
tf_matrix = tf.fit_transform(movies3['genres'])
cosine_sim = cosine_similarity(tf_matrix, tf_matrix)

def recommendation_genre(movie_df, similarity_matrix, movie_title, topN):
    indices = pd.Series(movie_df.index, index=movie_df['title'])
    index = indices[movie_title]
    cosine_score = list(enumerate(similarity_matrix[index]))
    cosine_score = sorted(cosine_score, key=lambda x: x[1], reverse=True)
    matched = [i[0] for i in cosine_score[1:topN+1]]  # Skip the first match (itself)
    matching_df = movie_df.iloc[matched]
    matching_df.rename(columns={'title': 'Movie Title'}, inplace=True)
    matching_df['Sno.'] = range(1, len(matching_df) + 1)
    matching_df.index = range(0, len(matching_df))
    return matching_df[['Sno.', 'Movie Title']]

# Interactive widgets
genres = Dropdown(options=list(set(movies['genres'])), description="Genres", style={"description_width": 'initial'})
num_reviews = IntText(description="Minimum Reviews", style={"description_width": 'initial'})
num_recommendations_1 = IntText(description="Number of Recommendations", style={"description_width": 'initial'})
b1 = Button(description="RECOMMEND ME", style={"description_width": 'initial'})
popularity_tab = VBox([genres, HBox([num_reviews, num_recommendations_1]), b1])

title = Textarea(description="Movie Title", style={"description_width": 'initial'})
num_recommendations_2 = IntText(description="Number of Recommendations", style={"description_width": 'initial'})
b2 = Button(description="RECOMMEND ME", style={"description_width": 'initial'})
content_tab = VBox([title, HBox([num_recommendations_2]), b2])

tabs = [popularity_tab, content_tab]
wid = widgets.Tab(tabs)

names = ['Popularity Based Recommendations', 'Content Based Recommendations']
[wid.set_title(i, title) for i, title in enumerate(names)]

def b1_clicked(b):
    global output
    output = TopNPopularMovies(genre=genres.value, threshold=num_reviews.value, topN=num_recommendations_1.value)
    display(output)

def b2_clicked(b):
    global output
    output = recommendation_genre(movie_df=movies3, similarity_matrix=cosine_sim, movie_title=title.value, topN=num_recommendations_2.value)
    display(output)

b1.on_click(b1_clicked)
b2.on_click(b2_clicked)

display(wid)