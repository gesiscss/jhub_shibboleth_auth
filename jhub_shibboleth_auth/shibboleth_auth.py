from hashlib import md5
from jupyterhub.auth import LocalAuthenticator
from jupyterhub.handlers.login import LogoutHandler
from jupyterhub.handlers import url_escape, url_concat
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
        user_data = {header: self.request.headers.get(header, "")
                     for header in self.authenticator.headers
                     if self.request.headers.get(header, "")}
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
        # display info for test purpose
        custom_html = """
                    <div class="service-login">
                    Testing, no login is possible.<br>
                    {}
                    </div>
                    """.format(user_data)
        self.finish(self._render(custom_html=custom_html))
        return

    def _render(self, login_error=None, username=None, custom_html=None):
        return self.render_template('login.html',
                                    next=url_escape(self.get_argument('next', default='')),
                                    username=username,
                                    login_error=login_error,
                                    custom_html=custom_html,
                                    login_url=self.settings['login_url'],
                                    authenticator_login_url=url_concat(
                                        self.authenticator.login_url(self.hub.base_url),
                                        {'next': self.get_argument('next', '')},
                                    ),
                                    )


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
