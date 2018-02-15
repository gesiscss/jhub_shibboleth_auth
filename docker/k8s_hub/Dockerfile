# https://github.com/jupyterhub/zero-to-jupyterhub-k8s/tree/v0.5/images/hub
FROM jupyterhub/k8s-hub:v0.6

# https://github.com/gesiscss/jhub_shibboleth_auth
RUN pip3 install --no-cache-dir git+git://github.com/gesiscss/jhub_shibboleth_auth.git@master#egg=jhub_shibboleth_auth
#RUN pip3 install --no-cache-dir https://github.com/gesiscss/binderhub/archive/master.zip