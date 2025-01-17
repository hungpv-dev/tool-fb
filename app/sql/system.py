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
    
    def create_account(self,data=None):
        from helpers.system import get_system
        system = get_system()
        data['system_id'] = system.get('id')
        return self.post(f"system-details",data=data)
    
    def update_account(self,id,data=None):
        return self.put(f"system-details/{id}",data=data)
    
    def push_message(self,id,messsage):
        return self.update_account(id,data={
            'message': messsage,
        })
    
