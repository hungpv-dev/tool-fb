import logging
import os

def config_log(log_dir='./temp/logs', log_filename='error.log', max_lines=1000):
    """
    Cấu hình log cho ứng dụng và tự động xử lý khi vượt quá số dòng quy định.
    log_dir: Thư mục lưu trữ log.
    log_filename: Tên file log.
    max_lines: Giới hạn số dòng trong file log.
    """
    import os
    import logging

    # Tạo thư mục log nếu chưa có
    os.makedirs(log_dir, exist_ok=True)

    # Đường dẫn đầy đủ tới file log
    log_file_path = os.path.join(log_dir, log_filename)

    # Kiểm tra số dòng trong file log và xử lý nếu cần (xoá 100 dòng đầu tiên)
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r', encoding='utf-8') as file:
            line_count = sum(1 for line in file)
        if line_count >= max_lines:
            remove_first_n_lines(log_file_path, 100)

    # Cấu hình logging
    handler = logging.FileHandler(log_file_path, encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    # Xóa tất cả các handler cũ
    for old_handler in logger.handlers[:]:
        logger.removeHandler(old_handler)
    
    # Chỉ giữ lại FileHandler
    logger.addHandler(handler)

    # Giảm mức log tổng thể
    logger.setLevel(logging.WARNING)

    # Tắt log từ các thư viện không mong muốn
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("tensorflow").setLevel(logging.ERROR)



def remove_first_n_lines(log_file_path, n):
    """
    Hàm này xoá n dòng đầu tiên trong file log.
    log_file_path: Đường dẫn đến file log.
    n: Số dòng muốn xoá.
    """
    try:
        # Đọc tất cả các dòng trong file log
        with open(log_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Giữ lại các dòng từ dòng thứ n trở đi
        lines = lines[n:]
        
        # Ghi lại các dòng còn lại vào file log
        with open(log_file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)
        
        logging.info(f"Removed first {n} lines from log file.")
    except Exception as e:
        logging.error(f"Error removing first {n} lines from log file: {str(e)}")


def read_log(log_dir='./temp/logs', log_filename='error.log'):
    """
    Hàm này đọc nội dung của file log và trả về dưới dạng chuỗi.
    log_dir: Thư mục chứa file log.
    log_filename: Tên file log.
    Trả về nội dung của file log.
    """
    log_file_path = os.path.join(log_dir, log_filename)
    
    try:
        # Kiểm tra nếu file log tồn tại
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            return "Log file does not exist."
    except Exception as e:
        return f"Error reading log file: {str(e)}"