from pages.home import main_page
from pages.fanpage import fanpage_page
from pages.newsfeed import newsfeed_page,newsfeed_page_list
from pages.post import post_page,post_page_list
from pages.logs import logs_page
from pages.settings import settings_page
from pages.login import login_page

router = {
    'home' : main_page,
    'fanpage' : fanpage_page,
    'newsfeed' : newsfeed_page,
    'newsfeed_page_list': newsfeed_page_list,
    'post': post_page,
    'post_page_list': post_page_list,
    'logs': logs_page,
    'settings': settings_page,
    'login': login_page,
}
