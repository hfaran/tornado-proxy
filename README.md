# tornado-vhost-proxy

HTTP Proxy Server for Proxying to Local Virtual Hosts

## Usage

* `sudo pip install tornado  # install tornado`
* Modify `vhost_map.json` to map hostnames to the port(s) required.
* `./proxy.py -p [port] -v [vhost_map.json]`

## Usage with `supervisord`

```bash
sudo pip install supervisor
# Modify the command in supervisord.conf as required
sudo mkdir /var/log/tornado-vhost-proxy
sudo chown -R $USER /var/log/tornado-vhost-proxy
supervisord -c supervisord.conf
```
