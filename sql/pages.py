from sql.model import Model

class Page(Model):
    def __init__(self):
        super().__init__()

    def insert(self, data=None):
        return self.post("pages/insert", data=data)

    def get_pages(self, params=None):
        return self.get("pages", params=params)

    def update_page(self, page_id, data):
        return self.put(f"pages/api/{page_id}", data=data)
    
    def page_old(self):
        return self.get(f"page-old")
    
    def update_time(self, page_id):
        return self.put(f"pages/time/{page_id}", {
            "updated_at" : True
        })