# https://github.com/jupyterhub/zero-to-jupyterhub-k8s/tree/v0.4/images/hub
FROM jupyterhub/k8s-hub:a27db6f

RUN pip3 --no-cache-dir install git+git://github.com/gesiscss/jhub_shibboleth_auth.git@master#egg=jhub_shibboleth_auth
