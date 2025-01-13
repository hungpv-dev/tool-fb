import os
import requests
# Hàm tải ảnh về
def download_image(url, temp_dir="./temp/images", temp_file="image.png"):
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