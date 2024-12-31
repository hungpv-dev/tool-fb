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
browser.get("https://www.facebook.com/permalink.php?story_fbid=pfbid02og9c73UfN12LyQPe79iwtr9YyNDmV64Tf4jndWnzpHiM1mBQnwapStY3BG6fpUJnl&id=100091838821588")
sleep(2)
crawl = Crawl(browser)
data = crawl.crawlContentPost({}, {
    'id': 'pfbid02og9c73UfN12LyQPe79iwtr9YyNDmV64Tf4jndWnzpHiM1mBQnwapStY3BG6fpUJnl',
    'link': 'https://www.facebook.com/permalink.php?story_fbid=pfbid02og9c73UfN12LyQPe79iwtr9YyNDmV64Tf4jndWnzpHiM1mBQnwapStY3BG6fpUJnl&id=100091838821588',
}, {}, newfeed = True)

print(json.dumps(data,indent=4))






