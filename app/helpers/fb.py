from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, unquote
import pyperclip
from selenium.webdriver.common.keys import Keys
import logging

def is_valid_link(href, post):
    """
    Kiểm tra xem URL có hợp lệ hay không:
    - Không chứa ID của bài viết.
    - Không phải là một tệp GIF.
    - Không phải là một URL của Facebook.
    """
    return post['id'] not in href and '.gif' not in href and 'https://www.facebook.com' not in href

def clean_url_keep_params(href):
    try:
        if not href:
            return None  # Nếu href không tồn tại, trả về None hoặc xử lý phù hợp

        # Giải mã URL nhiều lần để xử lý các ký tự mã hóa phức tạp
        while True:
            decoded_href = unquote(href)
            if decoded_href == href:  # Nếu giải mã không làm thay đổi gì, dừng lại
                break
            href = decoded_href

        # Phân tích URL
        parsed_url = urlparse(href)

        # Chuyển đổi các tham số từ query string
        query_params = parse_qs(parsed_url.query)

        # Loại bỏ tiền tố 'amp;' trong các khóa của tham số
        normalized_params = {
            (k.split(";")[-1] if ";" in k else k): v
            for k, v in query_params.items()
        }

        # Debug: In các tham số sau khi chuẩn hóa
        # print("Normalized Parameters:", normalized_params)

        # Chỉ giữ lại các tham số 'id' và 'story_fbid'
        filtered_params = {k: v for k, v in normalized_params.items() if k in ['id', 'story_fbid']}

        # Debug: Kiểm tra tham số sau khi lọc
        # print("Filtered Parameters:", filtered_params)

        # Tái cấu trúc URL
        cleaned_query = urlencode(filtered_params, doseq=True)
        cleaned_url = urlunparse((
            parsed_url.scheme,  # http hoặc https
            parsed_url.netloc,  # domain
            parsed_url.path,    # đường dẫn
            parsed_url.params,  # tham số bổ sung (ít khi dùng)
            cleaned_query,      # query string (tham số GET)
            parsed_url.fragment # anchor (#fragment)
        ))

        # Debug: Kiểm tra URL đã xử lý
        # print("Cleaned URL:", cleaned_url)

        return cleaned_url
    except Exception as e:
        # Nếu gặp lỗi, trả về href gốc
        logging.error(f"Lỗi khi xử lý URL: {e}")
        print(f"Lỗi khi xử lý URL: {e}")
        return href
    
def clean_facebook_url_redirect(url):
    if 'l.facebook.com/l.php?u=' in url:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if 'u' in query_params:
            return query_params['u'][0]
    return url

import re
def sanitize_text(text):
    # Lọc bỏ các ký tự nằm ngoài phạm vi BMP
    return re.sub(r'[^\u0000-\uFFFF]', '', text)

def copy_and_paste_text(text,element):
    sanitized_text = sanitize_text(text)  # Loại bỏ ký tự đặc biệt
    element.send_keys(sanitized_text)
    # pyperclip.copy(text)
    # element.send_keys(Keys.CONTROL, 'v')

def set_html_in_div(driver, element, html_content):
    driver.execute_script("arguments[0].innerHTML = arguments[1];", element, html_content)
    driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", element)