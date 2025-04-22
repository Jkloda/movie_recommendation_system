import faiss
import numpy as np
import pandas as pd
import json
from sentence_transformers import SentenceTransformer

class Indexer:
    def __init__(self):
        self.index = None
        self.metadata = {}
        self.index_dim = 384
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Use CPU version of Faiss (no GPU resources needed)
        self.index = faiss.IndexFlatL2(self.index_dim)
        
        try:
            # Try reading the index from file
            self.index = faiss.read_index('movie_index')
        except Exception as e:
            print(f"Error reading the index: {e}")
            self.index = faiss.IndexFlatL2(self.index_dim)
        
        try:
            # Try loading metadata
            with open("movie_metadata.json", "r") as f:
                self.metadata = json.load(f)
        except FileNotFoundError:
            print("Metadata file not found, starting with empty metadata.")

    def chunk_text(self, text, tokens=256):
        # Ensure the text is a string and not a boolean or any other type
        if isinstance(text, bool):
            text = str(text)
        
        text_split = text.split()
        chunks = [" ".join(text_split[i:i + tokens]) for i in range(0, len(text_split), tokens)]
        return chunks

    def create_dataframe(self):
        headers = [
            "genres", "keywords", "original_title", "overview", "popularity", 
            "release_date", "runtime", "spoken_languages", "title", "cast", "director"
        ]
        self.data = pd.read_csv('../data/movie_dataset.csv', usecols=headers).fillna("")

    def embed_movie(self, movies):
        # Ensure that the 'movies' input is treated as a string
        if isinstance(movies, bool):
            movies = str(movies)
        
        text_input = ''
        if isinstance(movies, str):
            text_input = movies
        else:
            for movie in movies:
                # Ensure all fields are converted to strings (in case of booleans or other types)
                text_input += f" {str(movie.get('title', ''))} {str(movie.get('original_title', ''))} {str(movie.get('genres', ''))} {str(movie.get('overview', ''))} {str(movie.get('keywords', ''))} {str(movie.get('actors', ''))} {str(movie.get('director', ''))} {str(movie.get('spoken_languages', ''))}"
        
        # Now we split and encode the text as chunks
        chunks = self.chunk_text(text_input)
        embeddings = self.model.encode(chunks, normalize_embeddings=True)
        return embeddings.mean(axis=0)
    
    def add_movies(self):
        for index, movie in self.data.iterrows():
            embedding = self.embed_movie(movie)
            embedding = np.expand_dims(embedding, axis=0)
            faiss.normalize_L2(embedding)
            self.index.add(embedding.astype(np.float32))
            self.metadata[str(index)] = f"{movie['title']}: {movie['overview']}"
        
        # Write the updated index and metadata
        faiss.write_index(self.index, 'movie_index')
        with open('movie_metadata.json', 'w') as f:
            json.dump(self.metadata, f)

    def search_similar(self, query, movies_searched=5):
        # Ensure the query is a string
        if isinstance(query, bool):
            raise ValueError("Query should be a string, not a boolean")
        
        query_embedding = self.embed_movie(query)
        _, indices = self.index.search(np.array([query_embedding], dtype=np.float32), movies_searched)
        
        results = []
        for i in indices[0]:
            movie_info = self.metadata.get(str(i), "No metadata available")
            results.append(movie_info)
        
        return results
