from jupyterhub.auth import LocalAuthenticator
from jupyterhub.handlers import url_escape, url_concat
# from jupyterhub.utils import url_path_join
from traitlets import Unicode
from tornado import web
from jhub_remote_user_authenticator.remote_user_auth import RemoteUserLoginHandler, RemoteUserAuthenticator

from jhub_shibboleth_auth.utils import add_system_user


class ShibbolethLoginHandler(RemoteUserLoginHandler):

    def get(self):
        eppn = self.request.headers.get(self.authenticator.eppn, "")
        email_addres = self.request.headers.get(self.authenticator.email, "")
        persistent_id = self.request.headers.get(self.authenticator.persistent_id, "")
        d = {'eppn': eppn, 'email': email_addres, 'persistent id': persistent_id}
        if persistent_id == "":
            # self.finish(self._render())
            # self.redirect('/hub/shibboleth_login')
            raise web.HTTPError(401)  # 401 Unauthorized or 403 Forbidden
        else:
            # display info for test purpose
            custom_html = """
            <div class="service-login">
            Testing, no login is possible.<br>
            {}
            </div>
            """.format(d)
            self.finish(self._render(custom_html=custom_html))
            return
            # TODO persistent_id <-> user
            # # Get User for username, creating if it doesn't exist
            # user = self.user_from_username(remote_user)
            # self.set_login_cookie(user)
            # self.redirect(url_path_join(self.hub.server.base_url, 'home'))

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
    # custom_html = Unicode(
    #     # https://jupyter.brynmawr.edu/hub/login
    #     # https://github.com/jupyterhub/jupyterhub/issues/1385
    #     default_value="""
    #     <div class="service-login">
    #         <a href="https://notebooks.gesis.org/login" class='btn btn-jupyter'>Login</a>
    #     </div>
    #     """,
    #     help="""
    #     HTML form to be overridden by authenticators if they want a custom authentication form.
    #
    #     Defaults to an empty string, which shows the default username/password form.
    #     """
    # )

    def get_handlers(self, app):
        return [
            (r'/login', ShibbolethLoginHandler),
        ]

    # def set_custom_html(self):
    #     self.custom_html = """
    #     <a href="https://notebooks.gesis.org/shibboleth_login">Shibboleth login</a>
    #     """


class ShibbolethLocalAuthenticator(ShibbolethAuthenticator, LocalAuthenticator):

    def add_system_user(self, user):
        super(ShibbolethLocalAuthenticator, self).add_system_user(user)
        name = user.name
        notebooks_folder = '/home/{}/notebooks'.format(name)
        add_system_user(name, notebooks_folder)
