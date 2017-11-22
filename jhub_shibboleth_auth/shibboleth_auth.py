from jupyterhub.auth import LocalAuthenticator
from jupyterhub.utils import url_path_join
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
        parts = persistent_id.split('!')
        persistent_id = '{}!{}'.format(parts[0].replace('/', '..'), parts[2])
        if persistent_id == "":
            # self.finish(self._render())
            # self.redirect('/hub/shibboleth_login')
            raise web.HTTPError(401)  # 401 Unauthorized or 403 Forbidden
        else:
            # Get User for username, creating if it doesn't exist
            user = self.user_from_username(persistent_id)
            self.set_login_cookie(user)
            self.redirect(url_path_join(self.hub.server.base_url, 'home'))


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

    def get_handlers(self, app):
        return [
            (r'/login', ShibbolethLoginHandler),
        ]


class ShibbolethLocalAuthenticator(ShibbolethAuthenticator, LocalAuthenticator):

    def add_system_user(self, user):
        super(ShibbolethLocalAuthenticator, self).add_system_user(user)
        name = user.name
        notebooks_folder = '/home/{}/notebooks'.format(name)
        add_system_user(name, notebooks_folder)
