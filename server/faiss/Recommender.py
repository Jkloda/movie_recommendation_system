from Indexer import Indexer
from Http import HttpLayer

# Object and methods to handle faiss classes (Martin)
class Recommender:
    # init instance variables (Martin)
    def __init__(self):
        self.recommendation = [] 
        self.httpLayer = HttpLayer()
        self.indexer = Indexer()

    # search and return index, based on favourites (Martin)
    def search_index(self, favourites):
        self.recommendation = []
        total_movies = len(favourites)
        index_results = self.indexer.search_similar(favourites, total_movies)
        self.recommendation.append(str(index_results))

    # call search index and send results to http class for use with llama prompting, return final results (Martin)
    async def get_recommendation(self, favourites):
        self.search_index(favourites)
        new_recommendations = await self.httpLayer.prompt_lama(self.recommendation[0])
        self.recommendation = []
        self.recommendation.append(new_recommendations.replace("\n", " ").replace("\\", ""))
        return self.recommendation
 