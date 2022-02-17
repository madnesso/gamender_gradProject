class Games:
    def __init__(self, name, genre, rating=0):
        self.name = name
        self.rating = rating
        self.genre = genre

    def addGame(self):
        return self.name


class User:
    def __int__(self, username, password):
        self.username = username
        self.password = password

    def register(self):
        pass

    def login(self):
        pass

    def reviewGame(self):
        pass

    def ChangedLikedGenre(self):
        pass
