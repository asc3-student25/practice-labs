from itertools import count

from backend.models import User


class UserStore:
    def __init__(self):
        self._users = {}
        self._ids = count(1)

    def create(self, username, email):
        user_id = next(self._ids)
        user = User(id=user_id, username=username, email=email)
        self._users[user_id] = user
        return user

    def get(self, user_id):
        return self._users.get(user_id)

    def list_all(self):
        return list(self._users.values())


store = UserStore()
