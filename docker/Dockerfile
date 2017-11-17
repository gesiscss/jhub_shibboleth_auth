# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# https://github.com/nginxinc/docker-nginx/blob/master/stable/stretch/Dockerfile
FROM nginx:1.13.6

MAINTAINER iLCM Project <kenan.erdogan@gesis.org>

USER root

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get -yq dist-upgrade -y && \
    apt-get autoremove -y && \
    apt-get autoclean -y && \
    apt-get install -yq --no-install-recommends \
    apt-utils \
    wget \
    vim \
    build-essential \
    fakeroot \
    htop \
    curl \
    supervisor \
    libshibsp-plugins \
    shibboleth-sp2-common \
    shibboleth-sp2-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# nginx
COPY ./nginx/packages/nginx-module-shibboleth_1.13.6-1_stretch_amd64.deb /tmp/
COPY ./nginx/packages/nginx-module-headersmore_1.13.6-1_stretch_amd64.deb /tmp/
RUN cd /tmp && \
    dpkg -i nginx-module-shibboleth_1.13.6-1_stretch_amd64.deb \
            nginx-module-headersmore_1.13.6-1_stretch_amd64.deb

COPY ./nginx/includes/shib_clear_headers /etc/nginx/shib_clear_headers
COPY ./nginx/includes/shib_fastcgi_params /etc/nginx/shib_fastcgi_params

# supervisor needs nginx starting in Foreground
#RUN sed -i "1idaemon off;" /etc/nginx/nginx.conf
# add new installed modules
RUN sed -i "1iload_module modules/ngx_http_headers_more_filter_module.so;" /etc/nginx/nginx.conf
RUN sed -i "1iload_module modules/ngx_http_shibboleth_module.so;" /etc/nginx/nginx.conf

# Shibboleth
RUN mkdir /var/run/shibboleth/ && \
    chown -R _shibd:_shibd /var/log/shibboleth /var/run/shibboleth/

# Copy supervisor config files
COPY ./supervisor /etc/supervisor

EXPOSE 80 443

# CMD ["nginx", "-g", "daemon off;"]
# CMD ["/usr/bin/supervisord", "--nodaemon", "--configuration", "/etc/supervisor/supervisord.conf"]
