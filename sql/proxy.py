from sql.model import Model

class Proxy(Model):
    def __init__(self):
        super().__init__()

    def all(self, params=None):
        return self.get("proxies", params=params)

    def insert(self, data):
        return self.post(f"proxies", data=data)
    
    def update(self,id,data):
        return self.put(f"proxies/{id}",data)
    
    def destroy(self, id):
        return self.delete(f"proxies/{id}")