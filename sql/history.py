from sql.model import Model

class HistoryCrawlPage(Model):
    def __init__(self):
        super().__init__()

    def insert(self, data):
        res = self.post("history-crawl-page", data=data)
        return res
    
    def update(self, history_id, data):
            return self.put(f"history-crawl-page/{history_id}", data=data)
        
    def update_count(self, history_id, data):
        return self.post(f"history-crawl-update-count/{history_id}", data=data)