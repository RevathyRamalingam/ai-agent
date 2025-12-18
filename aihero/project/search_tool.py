from typing import List,Any
class SearchTool:
    def __init__(self,index):
        self.index=index
    def search(self,query:str)-> List[Any]:
        #takes the query, searches the index to return matching top 5 results
        return self.index.search(query,num_results=5)