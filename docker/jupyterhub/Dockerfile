# https://github.com/jupyterhub/jupyterhub/blob/0.8.1/Dockerfile
FROM jupyterhub/jupyterhub:0.8.1

RUN pip --no-cache-dir install git+git://github.com/gesiscss/jhub_shibboleth_auth.git@master#egg=jhub_shibboleth_auth

ADD jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py