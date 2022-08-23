from contextvars import ContextVar


class AppContext:
    def __init__(self):
        self._username = None
        self._user = None

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username: str):
        self._username = username

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, user):
        self._user = user


app_context = ContextVar('app_context', default=AppContext()).get()
