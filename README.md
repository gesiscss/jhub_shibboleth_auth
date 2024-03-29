**This repo is not maintained anymore.**

# jhub_shibboleth_auth
Shibboleth authentication for JupyterHub.

## Installation

```bash
pip install jhub_shibboleth_auth
```

## Sources

For more information on nginx and Shibboleth SP with FastCGI support, check:

- https://wiki.shibboleth.net/confluence/display/SHIB2/Integrating+Nginx+and+a+Shibboleth+SP+with+FastCGI
- https://github.com/nginx-shib/nginx-http-shibboleth
- https://github.com/nginx-shib/nginx-http-shibboleth/blob/master/CONFIG.rst
- https://tcg.stanford.edu/?p=131

To run Shibboleth SP and nginx FastCGI in a docker container, check:

- https://github.com/gesiscss/jhub_shibboleth_auth/tree/master/docker/shibboleth
- https://github.com/gesiscss/jhub_shibboleth_auth/blob/master/docker/shibboleth/example-docker-compose.yaml

Shibboleth embedded discovery service: https://wiki.shibboleth.net/confluence/display/EDS10/1.+Overview

---

Funded by the German Research Foundation (DFG).
FKZ/project number:
[324867496](https://gepris.dfg.de/gepris/projekt/324867496?context=projekt&task=showDetail&id=324867496&).
