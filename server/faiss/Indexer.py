import faiss
import numpy as np
import pandas as pd
import json
from sentence_transformers import SentenceTransformer

# Faiss index object and methods (Martin)
class Indexer:
    # init model, index, gpu resources and load index and metadata into memory (Martin)
    def __init__(self):
        self.index = {}
        self.metadata = {}
        self.index_dim = 384
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        res = faiss.StandardGpuResources()
        self.index = faiss.IndexFlatL2(self.index_dim)
        self.index = faiss.read_index('movie_index')
        f = open("movie_metadata.json")
        self.metadata = json.load(f)
        self.index = faiss.index_cpu_to_gpu(res, 0, self.index)

    # chunk text for creating index (Martin)
    def chunk_text(self, text, tokens=256):
        text_split = text.split()
        chunks = [" ".join(text_split[i:i + tokens]) for i in range(0, len(text_split), tokens)]
        return chunks

    #create dataframe for data extraction and vectorisation (Martin)
    def create_dataframe(self):
        headers = ["genres", "keywords", "original_title", "overview", "popularity", "release_date", "runtime", "spoken_languages", "title", "cast", "director"]
        self.data = pd.read_csv('../data/movie_dataset.csv', usecols=headers).fillna("")

    # concatenate data columns, chunk text, get dot product of chunked vector array and return mean vector (Martin)
    def embed_movie(self, movies):
        text_input = ''
        if isinstance(movies, str):
            text_input = movies
        else: 
            for movie in movies:   
                text_input = f"{text_input} {movie['title']} {movie['original_title']} {movie['genres']} {movie['overview']} {movie['keywords']} {movie['actors']} {movie['director']} {movie['spoken_languages']} "
        print(text_input)
        chunks = self.chunk_text(text_input)
        embeddings = self.model.encode(chunks, normalize_embeddings=True)
        return embeddings.mean(axis=0)
    
    # add movies to index and metadata, then save index and metadata (Martin)
    def add_movies(self):
        for index, movie in self.data.iterrows(): 
            embedding = self.embed_movie(movie)
            embedding = np.expand_dims(embedding, axis=0)
            faiss.normalize_L2(embedding)
            self.index.add(embedding.astype(np.float32))
            self.metadata[index] = f"{movie['title']}: {movie['overview']}"
        self.index = faiss.index_gpu_to_cpu(self.index)
        faiss.write_index(self.index,'movie_index')
        with open('movie_metadata.json', 'w') as f:
           json.dump(self.metadata, f)
        
    # return matching semantic information (Martin)
    def search_similar(self, query, movies_searched):
        query_embedding = self.embed_movie(query)
        _, indices = self.index.search(np.array([query_embedding], dtype=np.float32), 5)
        results= ''
        for i in indices[0]:
            results = f'{results} [{self.metadata[str(i)]}]'
        return results