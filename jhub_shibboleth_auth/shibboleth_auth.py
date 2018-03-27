from jupyterhub.auth import LocalAuthenticator
from jupyterhub.handlers.login import LogoutHandler
from jupyterhub.crypto import decrypt
from jupyterhub.utils import url_path_join
from urllib.parse import urlparse
from traitlets import Unicode, List, validate, TraitError
from tornado import web, gen
from jhub_remote_user_authenticator.remote_user_auth import RemoteUserLoginHandler, RemoteUserAuthenticator

from jhub_shibboleth_auth.utils import add_system_user


class ShibbolethLoginHandler(RemoteUserLoginHandler):

    def _get_user_data_from_request(self):
        # print('HEADERS:', self.request.headers)
        # NOTE: The Persistent ID is a triple with the format:
        # <name for the source of the identifier>!
        # <name for the intended audience of the identifier >!
        # <opaque identifier for the principal >
        user_data = {}
        for i, header in enumerate(self.authenticator.headers):
            value = self.request.headers.get(header, "")
            if value:
                try:
                    # sometimes header value is in latin-1 encoding
                    # TODO what causes this? fix encoding in there
                    value = value.encode('latin-1').decode('utf-8')
                except UnicodeDecodeError:
                    pass
                user_data[header] = value
                if i == 0:
                    user_data['jh_name'] = value
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
            # TODO better solution
            # add decryption filter into templates
            self.settings['jinja2_env'].filters['decrypt'] = decrypt
            self.set_login_cookie(user)
            self.log.info("User logged in: %s", username)
            # print(user.get_auth_state())  # user.py
            self.redirect(self.get_next_url(user), permanent=False)

    def get_next_url(self, user=None):
        """Get the next_url for login redirect

        Defaults to hub home /hub/home.
        """
        next_url = self.get_argument('next', default='')
        if (next_url + '/').startswith('%s://%s/' % (self.request.protocol, self.request.host)):
            # treat absolute URLs for our host as absolute paths:
            next_url = urlparse(next_url).path
        if not next_url.startswith('/'):
            next_url = ''
        if not next_url:
            next_url = url_path_join(self.hub.base_url, 'home')
        return next_url


class ShibbolethLogoutHandler(LogoutHandler):
    """Log a user out by clearing their login cookie."""
    def get(self):
        user = self.get_current_user()
        if user:
            self.log.info("User logged out: %s", user.name)
            self.clear_login_cookie()
            self.statsd.incr('logout')
        self.redirect(self.authenticator.shibboleth_logout_url, permanent=False)
        # if self.authenticator.auto_login:
        #     html = self.render_template('logout.html')
        #     self.finish(html)
        # else:
        #     self.redirect(self.settings['login_url'], permanent=False)


class ShibbolethAuthenticator(RemoteUserAuthenticator):
    headers = List(
        default_value=['mail', 'Eppn', 'cn', 'Givenname', 'sn'],
        config=True,
        help="""List of HTTP headers to get user data. First item is used as unique user name."""
    )
    shibboleth_logout_url = Unicode(
        default_value='',
        config=True,
        help="""Url to logout from shibboleth SP.""")

    @validate('headers')
    def _valid_headers(self, proposal):
        if not proposal['value']:
            raise TraitError('Headers should contain at least 1 item.')
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
