from pages.home import main_page
from pages.fanpage import fanpage_page
from pages.newsfeed import newsfeed_page,newsfeed_page_list
router = {
    'home' : main_page,
    'fanpage' : fanpage_page,
    'newsfeed' : newsfeed_page,
    'newsfeed_page_list': newsfeed_page_list,
}