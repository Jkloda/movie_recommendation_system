import faiss
import numpy as np
import pandas as pd
import json
import os
import mysql.connector.pooling
from sentence_transformers import SentenceTransformer
import base64
from dotenv import load_dotenv
load_dotenv()

class Indexer:
    

    connection_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="moviefinder_pool",
        user=os.getenv('USER'),
        host=os.getenv('HOST'),
        password=os.getenv('PASS'),
        database=os.getenv('DATABASE')
    )

    def __init__(self):
        self.indexes = {}
        self.metadata = {}
        self.index_dim = 384
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        res = faiss.StandardGpuResources()
        #self.index = faiss.IndexFlatL2(self.index_dim)
        '''self.index = faiss.read_index('movie_index')
        f = open("movie_metadata.json")
        self.metadata = json.load(f)
        print("index: ", self.index.ntotal)
        print("meta: ", len(self.metadata))
        print("Metadata keys:", list(self.metadata.keys())[:10])'''
        #self.index = faiss.index_cpu_to_gpu(res, 0, self.index)

    def chunk_text(self, text, tokens=256):
        text_split = text.split()
        chunks = [" ".join(text_split[i:i + tokens]) for i in range(0, len(text_split), tokens)]
        return chunks

    def create_dataframe(self):
        headers = ["genres", "keywords", "original_title", "overview", "popularity", "release_date", "runtime", "spoken_languages", "title", "cast", "director"]
        self.data = pd.read_csv('../data/movie_dataset.csv', usecols=headers).fillna("")

    def create_indexes_and_meta_data(self):
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            genres_query = "SELECT * FROM genres ORDER BY genre;"
            get_movies_by_genre = "SELECT movies.*, GROUP_CONCAT(DISTINCT keywords.keyword) AS keywords, GROUP_CONCAT(DISTINCT genres.genre) AS genres, GROUP_CONCAT(DISTINCT actors.actor) as actors FROM movies \
                JOIN movies_keywords ON movies.id = movies_keywords.movies_id JOIN keywords ON movies_keywords.keywords_id = keywords.id \
                JOIN movies_genres ON movies.id = movies_genres.movies_id JOIN genres ON movies_genres.genres_id = genres.id \
                JOIN movies_actors ON movies.id = movies_actors.movies_id JOIN actors ON movies_actors.actors_id = actors.id \
                WHERE genres.genre = %s GROUP BY movies.id;"
            cursor.execute(genres_query)
            genres = cursor.fetchall()
            

            for i, genre in enumerate(genres):
                res = faiss.StandardGpuResources()
                self.indexes[i] = faiss.IndexFlatL2(self.index_dim)
                self.indexes[i] = faiss.index_cpu_to_gpu(res, 0, self.indexes[i])

                cursor.execute(get_movies_by_genre, (genre['genre'],))
                movie_data = cursor.fetchall()
                self.metadata[i] = {}
                for j, movie in enumerate(movie_data):
                    embedding = self.embed_movie(movie, True)
                    embedding = np.expand_dims(embedding, axis=0)
                    faiss.normalize_L2(embedding)
                    self.indexes[i].add(embedding.astype(np.float32))
                    self.metadata[i][j] = f"{movie['title']}: {movie['overview']}"
                

            
            '''get_movies = "SELECT movies.*, GROUP_CONCAT(DISTINCT keywords.keyword) AS keywords, GROUP_CONCAT(DISTINCT genres.genre) AS genres, GROUP_CONCAT(DISTINCT actors.actor) as actors FROM movies \
                JOIN movies_keywords ON movies.id = movies_keywords.movies_id JOIN keywords ON movies_keywords.keywords_id = keywords.id \
                JOIN movies_genres ON movies.id = movies_genres.movies_id JOIN genres ON movies_genres.genres_id = genres.id \
                JOIN movies_actors ON movies.id = movies_actors.movies_id JOIN actors ON movies_actors.actors_id = actors.id \
                WHERE genres.genre LIKE %s GROUP BY movies.id;"
            cursor.execute(get_movies, ('%',))
            movie_data = cursor.fetchall()
            index = {}
            metadata = {}
            res = faiss.StandardGpuResources()
            index = faiss.IndexFlatL2(self.index_dim)
            index = faiss.index_cpu_to_gpu(res, 0, index)
                
            for i, movie in enumerate(movie_data):
                embedding = self.embed_movie(movie, True) 
                embedding = np.expand_dims(embedding, axis=0)
                faiss.normalize_L2(embedding)
                index.add(embedding.astype(np.float32))
                metadata[i] = f"{movie['title']}: {movie['overview']}"'''
            
        except Exception as e:
            print(f'error creating indexes and metadata: {e}')
        finally:
            cursor.close()
            connection.close()


    def embed_movie(self, movie, load_system = False):
        if(load_system):
            text_input = f"{movie['title']} {movie['original_title']} {movie['genres']} {movie['overview']} {movie['keywords']} {movie['actors']} {movie['director']} {movie['spoken_languages']}" 
        else:
            if isinstance(movie, str):
                text_input = movie
            else:    
                text_input = f"{movie['title']} {movie['original_title']} {movie['genres']} {movie['overview']} {movie['keywords']} {movie['actors']} {movie['director']} {movie['spoken_languages']}"
        chunks = self.chunk_text(text_input)
        embeddings = self.model.encode(chunks, normalize_embeddings=True)
        return embeddings.mean(axis=0)
    
    def add_movies(self):
        for index, movie in self.data.iterrows():
            embedding = self.embed_movie(movie)
            print("Embedding shape:", embedding.shape)
            embedding = np.expand_dims(embedding, axis=0)
            faiss.normalize_L2(embedding)

            self.index.add(embedding.astype(np.float32))
            self.metadata[index] = f"{movie['title']}: {movie['overview']}"
        self.index = faiss.index_gpu_to_cpu(self.index)
        faiss.write_index(self.index,'movie_index')
        with open('movie_metadata.json', 'w') as f:
           json.dump(self.metadata, f)
        

    def search_similar(self, query, result_amount=10):
        query_embedding = self.embed_movie(query)
        _, indices = self.indexes[0].search(np.array([query_embedding], dtype=np.float32), result_amount)
        results= ''
        for i in indices[0]:
            results = f'{results} [{self.metadata[0][i]}]'
        return results