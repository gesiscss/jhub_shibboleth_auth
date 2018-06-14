from jupyterhub.auth import Authenticator, LocalAuthenticator
from jupyterhub.handlers import BaseHandler
from traitlets import Unicode, List, validate, TraitError
from tornado import web

from jhub_shibboleth_auth.utils import add_system_user


class ShibbolethLoginHandler(BaseHandler):

    def _get_user_data_from_request(self):
        """Get shibboleth attributes (user data) from request headers."""
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

    async def get(self):
        """Get user data and log user in."""
        self.statsd.incr('login.request')
        user_data = self._get_user_data_from_request()
        if user_data.get('jh_name') is None:
            raise web.HTTPError(403)

        user = await self.login_user(user_data)
        if user is None:
            raise web.HTTPError(403)
        else:
            self.redirect(self.get_next_url(user))


class ShibbolethLogoutHandler(BaseHandler):
    """Log a user out from JupyterHub by clearing their login cookie
    and then redirect to shibboleth logout url to clear shibboleth cookie."""
    def get(self):
        user = self.get_current_user()
        if user:
            self.log.info("User logged out: %s", user.name)
            self.clear_login_cookie()
            self.statsd.incr('logout')
        self.redirect(self.authenticator.shibboleth_logout_url)


class ShibbolethAuthenticator(Authenticator):
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

    async def authenticate(self, handler, data):
        """
        :param handler: the current request handler (ShibbolethLoginHandler)
        :param data: user data from request headers (shibboleth attributes)
        :return: User data dict in a form that login_user method can process it.
        'name' holds the username and 'auth_state' holds all data requested from shibboleth.
        """
        user_data = {
            'name': data['jh_name'],
            'auth_state': data
        }
        return user_data

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
