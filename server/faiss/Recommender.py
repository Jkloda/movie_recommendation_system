from Indexer import Indexer
from Http import HttpLayer

class Recommender:
    def __init__(self):
        self.recommendation = [] 
        self.httpLayer = HttpLayer()
        self.indexer = Indexer()

    def search_index(self, favourites):
        self.recommendation = []
        total_movies = len(favourites)
        index_results = self.indexer.search_similar(favourites, total_movies)
        self.recommendation.append(str(index_results))

    async def get_recommendation(self, favourites):
        self.search_index(favourites)
        new_recommendations = await self.httpLayer.prompt_lama(self.recommendation[0])
        self.recommendation = []
        self.recommendation.append(new_recommendations.replace("\n", " ").replace("\\", ""))
        return self.recommendation
 