
from facebook.crawl import Crawl
from base.browser import Browser
import json
from time import sleep
manager = Browser()
browser = manager.start(False)
browser.get("https://www.facebook.com/vibesinternacionais/posts/pfbid0VRaNca6GGTQmYQsHocabzXcFrBgyrZ8NAfBsn5WFV8VaemRgKvPjkHtPGsp6DjeVl?comment_id=1425277585297419")
sleep(2)
crawl = Crawl(browser)
data = crawl.crawlContentPost({}, {
    'id': 'pfbid0VRaNca6GGTQmYQsHocabzXcFrBgyrZ8NAfBsn5WFV8VaemRgKvPjkHtPGsp6DjeVl',
    'link': 'https://www.facebook.com/vibesinternacionais/posts/pfbid0VRaNca6GGTQmYQsHocabzXcFrBgyrZ8NAfBsn5WFV8VaemRgKvPjkHtPGsp6DjeVl?comment_id=1425277585297419',
}, {}, newfeed = True)

print(json.dumps(data,indent=4))


