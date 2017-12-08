from hashlib import md5
from jupyterhub.auth import LocalAuthenticator
from jupyterhub.handlers.login import LogoutHandler
from jupyterhub.crypto import decrypt
from traitlets import Unicode, List, validate, TraitError
from tornado import web, gen
from jhub_remote_user_authenticator.remote_user_auth import RemoteUserLoginHandler, RemoteUserAuthenticator

from jhub_shibboleth_auth.utils import add_system_user


class ShibbolethLoginHandler(RemoteUserLoginHandler):

    def __init__(self, *args, **kwargs):
        super(ShibbolethLoginHandler, self).__init__(*args, **kwargs)
        # TODO better solution
        # add decryption filter to templates
        self.settings['jinja2_env'].filters['decrypt'] = decrypt

    def _get_user_data_from_request(self):
        # print('HEADERS:', self.request.headers)
        # NOTE: The Persistent ID is a triple with the format:
        # <name for the source of the identifier>!
        # <name for the intended audience of the identifier >!
        # <opaque identifier for the principal >
        user_data = {header: self.request.headers.get(header, "") for header in self.authenticator.headers}
        if user_data.get('persistent-id'):
            user_data['jh_name'] = md5(user_data['persistent-id'].encode()).hexdigest()
        return user_data

    @gen.coroutine
    def _save_auth_state(self, user, auth_state):
        """taken from handlers/base.py login_user() method"""
        # always set auth_state and commit,
        # because there could be key-rotation or clearing of previous values
        # going on.
        if not self.authenticator.enable_auth_state:
            # auth_state is not enabled. Force None.
            auth_state = None
        yield user.save_auth_state(auth_state)
        self.db.commit()

    def get(self):
        user_data = self._get_user_data_from_request()
        username = user_data.get('jh_name')
        if username is None:
            raise web.HTTPError(401)  # 401 Unauthorized or 403 Forbidden
        else:
            # Get User for username, creating if it doesn't exist
            user = self.user_from_username(username)
            self._save_auth_state(user, user_data)
            self.set_login_cookie(user)
            self.log.info("User logged in: %s", username)
            # print(user.get_auth_state())  # user.py
            self.redirect(self.get_next_url(user), permanent=False)


class ShibbolethLogoutHandler(LogoutHandler):
    """Log a user out by clearing their login cookie."""
    def get(self):
        user = self.get_current_user()
        if user:
            self.log.info("User logged out: %s", user.name)
            self.clear_login_cookie()
            self.statsd.incr('logout')
        self.redirect(self.authenticator.shibboleth_logout_url)
        # if self.authenticator.auto_login:
        #     html = self.render_template('logout.html')
        #     self.finish(html)
        # else:
        #     self.redirect(self.settings['login_url'], permanent=False)


class ShibbolethAuthenticator(RemoteUserAuthenticator):
    headers = List(
        default_value=['persistent-id', 'mail', 'Eppn'],
        config=True,
        help="""List of HTTP headers to get user data. 
        This must contain persistent-id, because it is used to create unique user name."""
    )
    shibboleth_logout_url = Unicode(
        default_value='',
        config=True,
        help="""Url to logout from shibboleth SP.""")

    @validate('headers')
    def _valid_headers(self, proposal):
        if 'persistent-id' not in proposal['value']:
            raise TraitError('Headers should contain "persistent-id"')
        return proposal['value']

    def get_handlers(self, app):
        return [
            (r'/login', ShibbolethLoginHandler),
            (r'/logout', ShibbolethLogoutHandler),
        ]


class ShibbolethLocalAuthenticator(ShibbolethAuthenticator, LocalAuthenticator):

    def add_system_user(self, user):
        super(ShibbolethLocalAuthenticator, self).add_system_user(user)
        name = user.name
        notebooks_folder = '/home/{}/notebooks'.format(name)
        add_system_user(name, notebooks_folder)
