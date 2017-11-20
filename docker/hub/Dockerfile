# https://github.com/jupyterhub/zero-to-jupyterhub-k8s/tree/v0.4/images/hub
FROM jupyterhub/k8s-hub:v0.4

RUN pip3 --no-cache-dir install git+git://github.com/gesiscss/jhub_shibboleth_auth.git@dev#egg=jhub_shibboleth_auth

ADD jupyterhub_config.py /srv/jupyterhub_config.py