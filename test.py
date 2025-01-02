# from helpers.time import convert_to_db_format

# time_strings = ["13h"]
# import re
# # In kết quả
# for original in time_strings:   
#     cleaned_text = re.sub(r'[^a-zA-Z0-9 ]', '', original)
#     converted = convert_to_db_format(cleaned_text)
#     print(f"Original: {original} -> Converted for DB: {converted}")




from facebook.crawl import Crawl
from base.browser import Browser
import json
from time import sleep
manager = Browser()
browser = manager.start(False)
browser.get("https://www.facebook.com/Bosschicksnews/posts/pfbid024CVJ1uvizCbWBqEx6VCy3P3dLPN9gyTk7jzd7i9F7tqwCTTaptJipffmuzSJ8vRKl")
sleep(2)
crawl = Crawl(browser)
data = crawl.crawlContentPost({}, {
    'id': 'pfbid024CVJ1uvizCbWBqEx6VCy3P3dLPN9gyTk7jzd7i9F7tqwCTTaptJipffmuzSJ8vRKl',
    'link': 'https://www.facebook.com/Bosschicksnews/posts/pfbid024CVJ1uvizCbWBqEx6VCy3P3dLPN9gyTk7jzd7i9F7tqwCTTaptJipffmuzSJ8vRKl',
}, {}, newfeed = True)

print(json.dumps(data,indent=4))
sleep(1000)






