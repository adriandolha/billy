class AuthenticationException(Exception):
    def __init__(self):
        self.message = 'Authentication error.'
        super().__init__(self.message)


class AuthorizationException(Exception):
    def __init__(self):
        super().__init__('Authentication error.')
