import win32clipboard
import win32con
from PIL import Image
import io
import os
import requests

def copy_image_to_clipboard(image_path_or_url):
    try:
        if image_path_or_url.startswith("http"):
            print("Tải ảnh từ URL...")
            response = requests.get(image_path_or_url)
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
            else:
                print(f"Lỗi tải ảnh: {response.status_code}")
                return
        else:
            print("Mở ảnh từ thư mục...")
            img = Image.open(image_path_or_url)

        print("Chuyển ảnh sang định dạng DIB...")
        output = io.BytesIO()
        img.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]  # Cắt phần header 14 bytes của BMP
        output.close()

        # Đưa ảnh vào clipboard
        print("Đưa ảnh vào clipboard...")
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_DIB, data)  # Sử dụng đúng định dạng DIB
        win32clipboard.CloseClipboard()
        print("Ảnh đã được sao chép vào clipboard!")
    except Exception as e:
        print(f"Đã có lỗi xảy ra: {e}")

# Thử sao chép ảnh từ URL
# copy_image_to_clipboard('https://toigingiuvedep.vn/wp-content/uploads/2023/03/anh-nguoi-dep-trung-quoc.jpg')


# Hàm tải ảnh về
def download_image(url, temp_dir="./images", temp_file="image.png"):
    os.makedirs(temp_dir, exist_ok=True)  # Tạo thư mục tạm nếu chưa có
    temp_path = os.path.join(temp_dir, temp_file)
    response = requests.get(url)
    if response.status_code == 200:
        with open(temp_path, 'wb') as file:
            file.write(response.content)
        return os.path.abspath(temp_path)
    else:
        raise Exception(f"Không thể tải ảnh từ {url}")

# Hàm xóa file sau khi dùng xong
def delete_image(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)