# from helpers.time import convert_to_db_format

# time_strings = ["9h", "Yesterday at 10:43 AM", "2 days ago", '40m']
# import re
# # In kết quả
# for original in time_strings:   
#     cleaned_text = re.sub(r'[^a-zA-Z0-9 ]', '', original)
#     converted = convert_to_db_format(cleaned_text)
#     print(f"Original: {original} -> Converted for DB: {converted}")

# from facebook.crawlid import CrawlId
# from base.browser import Browser
# manager = Browser()
# browser = manager.start(False)
# browser.get("https://www.facebook.com/viralbox777")
# crawlid = CrawlId(browser)
# name = crawlid.updateInfoFanpage({
#     'id': 1602,
#     'link': 'https://www.facebook.com/BlackRappersMusicvn1'})

# print(name)



from base.browser import Browser
from facebook.push import Push
manager = Browser()
browser = manager.start(False)


