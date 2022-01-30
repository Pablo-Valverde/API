class cachedfile(list):

    def __init__(self, path) -> None:
        super().__init__()
        self.path = path
        self.update()

    def update(self):
        buffer = self.__update__()
        if not buffer: return
        self.clear()
        self += buffer

    def __update__(self):
        buffer = []
        try:
            with open(self.path, "r", encoding="UTF-8") as file:
                buffer = file.readlines()
        except (FileNotFoundError, PermissionError):
            pass
        return buffer
