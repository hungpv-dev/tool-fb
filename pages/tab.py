class Tab:
    def __init__(self, name, thread, browser):
        self.name = name
        self.thread = thread
        self.browser = browser
        self.is_open = True

    def close(self):
        """Đóng tab"""
        self.is_open = False
        if self.browser:
            self.browser.quit()
        print(f"Đã đóng tab: {self.name}")
