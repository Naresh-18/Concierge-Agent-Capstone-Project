import requests
from src.config import settings

class RecipeTool:
    def search(self, query: str):
        sample = {
            "title": "Mixed Veg Stir Fry",
            "ingredients": ["carrot", "beans", "peas", "oil", "salt"],
            "steps": ["chop veggies", "heat oil", "stir-fry 5 mins", "season"]
        }
        return {"status": "ok", "recipe": sample, "query": query}

class WebSearchTool:
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.cse_id = settings.GOOGLE_CSE_ID
        self.endpoint = "https://www.googleapis.com/customsearch/v1"

    def search(self, query: str):
        if self.api_key and self.cse_id:
            params = {"q": query, "key": self.api_key, "cx": self.cse_id}
            r = requests.get(self.endpoint, params=params, timeout=10)
            items = r.json().get("items", [])
            results = [{"title": i.get("title"), "link": i.get("link")} for i in items[:5]]
            return {"status": "ok", "results": results}
        return {"status": "mock", "results": [f"Result for {query}"]}
        
class ShoppingTool:
    def create_list(self, query: str):
        return {"status": "ok", "items": ["rice", "dal", "veggies"], "query": query}
