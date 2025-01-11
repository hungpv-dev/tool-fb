from sql.model import Model

class NewFeedModel(Model):
    def __init__(self):
        super().__init__()

    def all(self, params=None):
        return self.get("newsfeed", params=params)

    def first(self, params=None):
        return self.get("newsfeed-first", params=params)
    
    def insert(self, data):
        return self.post("newsfeed", data=data)
    
    def update(self, id, data):
        return self.put(f"newsfeed/{id}", data=data)
    
    def destroy(self, id):
        return self.delete(f"newsfeed/{id}")