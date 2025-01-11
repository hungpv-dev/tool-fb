from tools.driver import Browser
from tools.facebooks.crawl_content_post import CrawlContentPost
from time import sleep
from helpers.modal import closeModal
import json

manager = Browser('/newsfeed/75/710e55ef-e0e0-4f05-b0bc-14e8fc0316d7','./temp/extensions/207_135_205_96.zip')
browser = manager.start(False)
crawl_instance = CrawlContentPost(browser)
up = {
    'id': 'pfbid0tnszkCwtvpPGWcSApZDbuX1cPEz4RB2mVAafpAceF8Aou9ZZixZ8zCLByQfY5zFvl',
    'link': 'https://www.facebook.com/TapChiFootballVN/posts/pfbid0tnszkCwtvpPGWcSApZDbuX1cPEz4RB2mVAafpAceF8Aou9ZZixZ8zCLByQfY5zFvl',
}
browser.get(up['link'])
sleep(1)
data = crawl_instance.crawlContentPost({},up,{},True)
print(json.dumps(data,indent=4))
browser.quit()