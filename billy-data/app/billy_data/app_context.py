from contextvars import ContextVar


class AppContext:
    def __init__(self):
        self._username = None

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username: str):
        self._username = username


app_context = ContextVar('app_context', default=AppContext()).get()
