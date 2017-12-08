# https://github.com/jupyterhub/zero-to-jupyterhub-k8s/tree/e9673caac14bac72007afe91f2808679b81f1b20/images/hub
FROM jupyterhub/k8s-hub:v0.5.0

# https://github.com/gesiscss/jhub_shibboleth_auth
RUN pip3 install --no-cache-dir git+git://github.com/gesiscss/jhub_shibboleth_auth.git@local#egg=jhub_shibboleth_auth
#RUN pip3 install --no-cache-dir https://github.com/gesiscss/binderhub/archive/master.zip