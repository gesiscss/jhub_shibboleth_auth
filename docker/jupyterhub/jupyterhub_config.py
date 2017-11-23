# jupyterhub_config.py
c = get_config()

import os
pjoin = os.path.join

runtime_dir = os.path.dirname(os.path.realpath(__file__))

c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.port = 8000
c.JupyterHub.open_browser = False

# put the JupyterHub cookie secret and state db
# in /var/run/jupyterhub
c.JupyterHub.cookie_secret_file = pjoin(runtime_dir, 'cookie_secret')
c.JupyterHub.db_url = pjoin(runtime_dir, 'jupyterhub.sqlite')

# create system users that don't exist yet
c.LocalAuthenticator.create_system_users = True

c.Spawner.notebook_dir = '~/notebooks'
c.Spawner.args = ['--NotebookApp.default_url=/notebooks']

from jhub_shibboleth_auth import shibboleth_auth
c.JupyterHub.authenticator_class = shibboleth_auth.ShibbolethLocalAuthenticator
