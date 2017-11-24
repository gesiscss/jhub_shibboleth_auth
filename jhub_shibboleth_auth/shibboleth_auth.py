from hashlib import md5
from jupyterhub.auth import LocalAuthenticator
from jupyterhub.utils import url_path_join
from jupyterhub.handlers.login import LogoutHandler
from traitlets import Unicode
from tornado import web
from jhub_remote_user_authenticator.remote_user_auth import RemoteUserLoginHandler, RemoteUserAuthenticator

from jhub_shibboleth_auth.utils import add_system_user


class ShibbolethLoginHandler(RemoteUserLoginHandler):

    def get(self):
        print('HEADERS:', self.request.headers)
        # eppn = self.request.headers.get(self.authenticator.eppn, "")
        # email_addres = self.request.headers.get(self.authenticator.email, "")
        persistent_id = self.request.headers.get(self.authenticator.persistent_id, "")
        # NOTE: The Persistent ID is a triple with the format:
        # <name for the source of the identifier>!
        # <name for the intended audience of the identifier >!
        # <opaque identifier for the principal >
        if persistent_id == "":
            # self.finish(self._render())
            # self.redirect('/hub/shibboleth_login')
            raise web.HTTPError(401)  # 401 Unauthorized or 403 Forbidden
        else:
            # Get User for username, creating if it doesn't exist
            user_hash = md5(persistent_id.encode()).hexdigest()
            user = self.user_from_username(user_hash)
            self.set_login_cookie(user)
            self.redirect(self.hub.server.hub_prefix)


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
    eppn = Unicode(
        default_value='Eppn',
        config=True,
        help="""HTTP header to inspect for the authenticated EPPN.""")
    email = Unicode(
        default_value='mail',
        config=True,
        help="""HTTP header to inspect for the authenticated email.""")
    persistent_id = Unicode(
        default_value='persistent-id',
        config=True,
        help="""HTTP header to inspect for the authenticated persistent id.""")
    shibboleth_logout_url = Unicode(
        default_value='https://notebooks.gesis.org/Shibboleth.sso/Logout?return=https://idp.gesis.org/idp/profile/Logout',
        config=True,
        help="""Logout url from SP and IdP.""")

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



