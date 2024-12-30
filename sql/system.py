from sql.model import Model

class System(Model):
    def __init__(self):
        super().__init__()

    def all(self, params=None):
        return self.get("systems", params=params)

    def insert(self, data):
        return self.post(f"systems", data=data)
    
    def update(self,id,data):
        return self.put(f"systems/{id}",data)
    
    def update_count(self,id):
        return self.update(id,{
            'updateCount': True
        })
    
    def destroy(self, id):
        return self.delete(f"systems/{id}")