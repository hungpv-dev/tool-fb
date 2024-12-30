import dateparser
def convert_to_db_format(time_string):
        parsed_time = dateparser.parse(time_string)
        if parsed_time:
            # Định dạng lại thành dạng lưu database (YYYY-MM-DD HH:MM:SS)
            return parsed_time.strftime("%Y-%m-%d %H:%M:%S")
        return None  
