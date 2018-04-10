This docker file extends [JupyterHub's docker file for k8s](https://github.com/jupyterhub/zero-to-jupyterhub-k8s/tree/master/images/hub) with installation of `jhub_shibboleth_auth`.

Link to docker hub is [here](https://hub.docker.com/r/gesiscss/k8s-hub/) and link to extended image's hub is [here](https://hub.docker.com/r/jupyterhub/k8s-hub/tags/)

When you want to use `jhub_shibboleth_auth` in your JupyterHub on Kubernetes, you have to add these data into your `config.yaml`:

```yaml
hub:
  image:
    name: gesiscss/k8s-hub
    tag: v0.6-1289b9f8
  extraConfig: |
    c.Authenticator.shibboleth_logout_url = 'your Shibboleht logout url'
    c.Authenticator.enable_auth_state = True
auth:
  type: custom
  custom:
    className: "jhub_shibboleth_auth.shibboleth_auth.ShibbolethAuthenticator"
```