import os
from typing import List

import numpy as np
import pandas as pd
from pandas import Series
from pandas.core.interchange.dataframe_protocol import DataFrame

dataset_path = "/home/roman/PycharmProjects/movieRecomendationBot/recommendation/ml-100k"

r_cols = ['user_id', 'movie_id', 'rating', 'unix_timestamp']
i_cols = ['movie_id', 'movie title' ,'release date','video release date', 'IMDb URL', 'unknown', 'Action', 'Adventure',
 'Animation', 'Children\'s', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy',
 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
score_df = pd.read_csv(os.path.join(dataset_path, "ua.base"), sep='\t', names = r_cols, encoding='latin-1')
item_df = pd.read_csv(os.path.join(dataset_path, "u.item"), sep='|', names = i_cols, encoding='latin-1')
genres_df = pd.read_csv(os.path.join(dataset_path, "u.genre"), sep='|', names = ["genre", "index"],  encoding='latin-1')
genres_list = list(genres_df["genre"])

def get_genres(movie : Series) -> List[str]:
  genres = []
  for i, v in movie.items():
    if v == 1:
      genres.append(i)
  return genres

def get_movies_with_similiar_genres(df : pd.DataFrame, movie_name : str, genre_list : List[str] = genres_list, min_genres : int = 2) -> List[str]:
    print(movie_name)
    other_movies_items = df[df['movie title'] != movie_name]
    movie_item = df[df['movie title'] == movie_name][genres_list].iloc[0, :]
    target_genres = get_genres(movie_item)
    similiar_movies = []
    for index, row in other_movies_items.iterrows():
        nm = row['movie title']
        mv = row[genres_list]
        genres = get_genres(mv)
        intersection_genres = set(target_genres) & set(genres)
        if len(intersection_genres) >= min_genres:
            similiar_movies.append(row['movie title'])

    return similiar_movies

def pearson_correlation(table : pd.DataFrame, movie_name : str, similiar_movies : List[str]) -> Series:
  df = table[similiar_movies]
  df = df.loc[:,~df.columns.duplicated()].copy()
  y = table.loc[:, movie_name].to_numpy()
  result = pd.Series(dtype=object)

  for column in df.columns:
      if column != movie_name:
        x = df.loc[:, column].to_numpy()
        x_sum = 0
        y_sum = 0
        c = 0
        for i in range(len(x)):
          if np.isnan(x[i]) or np.isnan(y[i]):
            continue
          else:
            x_sum += x[i]
            y_sum += y[i]
            c += 1
        corr = 0
        if c > 0:
          x_mean = x_sum / c
          y_mean = y_sum / c
          cov = 0
          std_x = 0
          std_y = 0
          for j in range(len(x)):
            if np.isnan(x[j]) or np.isnan(y[j]):
              continue
            diff_x = x[j]-x_mean
            diff_y = y[j]-y_mean
            cov += diff_x*diff_y
            std_x += diff_x**2
            std_y += diff_y**2
          if std_x*std_y != 0:
            corr = cov / (std_x*std_y)**(0.5)
        result.loc[column] = corr
  return result


def full_pipeline(movie_name : str, df : pd.DataFrame = item_df, topn : int=10, genre_df : DataFrame=genres_df, min_genres : int =2) -> Series:

  """полный пайплайн для получения уже готовой рекомендации"""

  id_title_pairs = [pair for pair in zip(df['movie_id'], df['movie title'])]

  '''создаем таблицу '''

  movie_user_df = score_df.merge(df[['movie_id', 'movie title']], left_on='movie_id', right_on='movie_id')
  movie_user_df['id_title_pair'] = [pair for pair in zip(movie_user_df['movie_id'], movie_user_df['movie title'])]

  user_movie_table = pd.pivot_table(movie_user_df, columns=['id_title_pair'], values=['rating'], index = ['user_id'])

  '''освобождаемся от мульти индекса'''

  user_movie_table = user_movie_table.droplevel(0, axis=1)
  user_movie_table.index.name = None
  user_movie_table.columns.name = None

  ''' изменяем имена на название фильмов '''

  new_names = {}
  for column in user_movie_table.columns:
    new_names[column] = tuple(column)[1]
  user_movie_table.rename(columns=new_names, inplace=True)

  unrated_movies = df[~df['movie_id'].isin(score_df['movie_id'])] # нашел фильмы которые не были оценены никем

  for movie in zip(unrated_movies['movie_id'], unrated_movies['movie title']):
   user_movie_table[movie[1]] = movie[0] # добавляем не оцененные фильмы user_movie_table[movie] = 'NaN'

  genre_list = list(genre_df["genre"]) #все доступные жанры

  user_movie_table = user_movie_table.loc[:,~user_movie_table.columns.duplicated()].copy() #убираем дубликаты из таблицы на всякий случай

  similiar_movies_by_genre = get_movies_with_similiar_genres(df, movie_name, genre_list=genre_list, min_genres=min_genres) # ищем фильмы у которых есть совпадение по жанрам

  similiar_movies = pearson_correlation(user_movie_table, movie_name, similiar_movies_by_genre) # ищем корреляцию пирсона таргет фильма к уже выбранному списку фильмов

  return similiar_movies.sort_values(ascending=False)[:topn] # отбираем topn фильмов с наибольшей корреляцией

if __name__ == '__main__':
    print(full_pipeline("Toy Story (1995)"))