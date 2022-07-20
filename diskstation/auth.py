import requests


# login class
class Auth(object):
    def __init__(self, base_url, user, password):
        self.base_url = base_url
        self.user = user
        self.password = password
        self.session_id = None

    def login(self):
        login_url = self.base_url + 'auth.php?api=SYNO.PhotoStation.Auth&method=login&version=1&username=' + \
                    str(self.user) + '&password=' + str(self.password)
        try:
            res = requests.get(login_url).json()
            self.session_id = res['data']['sid']
        except Exception as e:
            self.session_id = None

    def is_logged_in(self):
        return self.session_id is not None
