# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 14:31:38 2020

@author: maria
"""
# This code was taken from a different source to construct a preditive model for doing movies suggestions
# REFERENCES: https://www.datacamp.com/community/tutorials/recommender-systems-python


def recommender(title, df1, df2):
    import pandas as pd
    import numpy as np

    df1.columns = ['id', 'tittle', 'cast', 'crew']
    df2 = df2.merge(df1, on='id')
    metadata = df2

    # Import TfIdfVectorizer from scikit-learn
    from sklearn.feature_extraction.text import TfidfVectorizer

    # Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
    tfidf = TfidfVectorizer(stop_words='english')

    # Replace NaN with an empty string
    metadata['overview'] = metadata['overview'].fillna('')

    # Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_matrix = tfidf.fit_transform(metadata['overview'])

    # Output the shape of tfidf_matrix
    tfidf_matrix.shape

    # Array mapping from feature integer indices to feature name.
    tfidf.get_feature_names()[5000:5010]

    # Import linear_kernel
    from sklearn.metrics.pairwise import linear_kernel

    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Construct a reverse map of indices and movie titles
    indices = pd.Series(metadata.index, index=metadata['title']).drop_duplicates()

    # Function that takes in movie title as input and outputs most similar movies
    def get_recommendations(title, cosine_sim=cosine_sim):
        # Get the index of the movie that matches the title
        idx = indices[title]

        # Get the pairwsie similarity scores of all movies with that movie
        sim_scores = list(enumerate(cosine_sim[idx]))

        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the scores of the 10 most similar movies
        sim_scores = sim_scores[1:11]

        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]

        # Return the top 10 most similar movies
        return metadata['title'].iloc[movie_indices]

    return get_recommendations(title)
