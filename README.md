## HTTP Proxy Server for Proxying to Local Virtual Hosts

Built using Tornado (tested with version 3.2), supports HTTP GET, and POST methods.

### Setup

    python setup.py install

### Usage

* Modify `vhost_map.json` to map hostnames to the port(s) required.
* `python tornado_proxy/proxy.py -p [port] -v [vhost_map.json]`

