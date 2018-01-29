This docker file extends [JupyterHub's docker file](https://github.com/jupyterhub/jupyterhub/blob/master/Dockerfile) with installation of `jhub_shibboleth_auth`.

Link to docker hub: https://hub.docker.com/r/gesiscss/jupyterhub/

## How to run this docker image

Example `jupyterhub_config.py`:

```python
c = get_config()

import os
pjoin = os.path.join

c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.port = 8000
c.JupyterHub.open_browser = False

runtime_dir = os.path.dirname(os.path.realpath(__file__))
c.JupyterHub.cookie_secret_file = pjoin(runtime_dir, 'cookie_secret')
c.JupyterHub.db_url = pjoin(runtime_dir, 'jupyterhub.sqlite')

c.LocalAuthenticator.create_system_users = True

c.Spawner.notebook_dir = '~/notebooks'
c.Spawner.args = ['--NotebookApp.default_url=/notebooks']

# auth
from jhub_shibboleth_auth import shibboleth_auth
c.JupyterHub.authenticator_class = shibboleth_auth.ShibbolethLocalAuthenticator
c.Authenticator.shibboleth_logout_url = "your Shibboleht logout url"
```

### First way

You can run the docker image with mounting `jupyterhub_config.py`:

`docker run -it --rm -p 8000:8000 -v path/to/jupyterhub_config.py:/srv/jupyterhub/jupyterhub_config.py <image_name>`

### Second way

You can extend this docker file and add your config file there:

```
FROM gesiscss/jupyterhub:v0.8.1

ADD jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py
```