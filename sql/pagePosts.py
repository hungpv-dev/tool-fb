from sql.model import Model

class PagePosts(Model):
    def __init__(self):
        super().__init__()

    def get_list(self, params=None):
        return self.get("page-posts", params=params)

    def update_data(self, pp_id, data):
        return self.put(f"page-posts/{pp_id}", data=data)
    
    def update_status(self, pp_id, data):
        return self.put(f"page-posts-status/{pp_id}", data=data)
    
    def first(self, params=None):
        return self.get(f"page-posts-first", params=params)
    
    def get_post_time(self, params=None):
        return self.get(f"page-posts-time", params=params)
    
    def get_post_list(self, params=None):
        return self.get(f"page-posts-list-page", params=params)
    
    def get_page_up(self, params=None):
        return self.get(f"page-posts-up", params=params)
    
    def update_next(self, data=None):
        return self.post(f"page-posts-up", data=data)