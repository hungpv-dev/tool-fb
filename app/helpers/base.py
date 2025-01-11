from router import router

def redirect(page_name):
    frame = router.get(page_name)()
    if frame is None:
        raise ValueError(f"Frame '{page_name}' không được khởi tạo.")
    frame.tkraise()
