This docker file is to run Shibboleth SP and nginx FastCGI in a docker container.

Link to docker hub: https://hub.docker.com/r/bitnik/nginx_shibboleth/

## Versions

- OS: Debian 9 (stretch)
- nginx:1.13.6
- Shibboleth SP: 2.6

## Sources

- The include files under `shibboleth/nginx/includes/` are taken from https://github.com/nginx-shib/nginx-http-shibboleth/tree/master/includes.
- Supervisor configuration files are based on https://bitbucket.org/hellomatter/shibboleth-nginx/src/5ebbc3ac5ac0c8101997dd26764e6c700f302d60/supervisor/?at=master.

## How to run the image

Example command:
```
sudo docker run -it --rm \
    -v path/to/shibboleth:/etc/shibboleth \
    -v path/to/shibboleth_nginx.conf:/etc/nginx/conf.d/shibboleth_nginx.conf \
    -v path/to/embedded_discovery_service:/home/shibboleth/embedded_discovery_service \
    -v /etc/letsencrypt:/etc/letsencrypt \
    -v /etc/ssl:/etc/ssl \
    -p 80:80 \
    -p 443:443 \
    nginx_shibboleth /bin/bash  -c "$(cat ./start-supervisor.sh)"
```

Check [example-docker.compose.yaml](https://github.com/gesiscss/jhub_shibboleth_auth/blob/master/docker/shibboleth/example-docker-compose.yaml) to see how to run JupyterHub with Shibboleth login in docker containers in swarm mode. It will create 3 containers: `jhub`, `nginx-shibboleth` and docker `visualizer`.

Shibboleth embedded discovery service: https://wiki.shibboleth.net/confluence/display/EDS10/1.+Overview
