#!/usr/bin/env python

"""HTTP Proxy Server for Proxying to Local Virtual Hosts"""


import random
import json
import argparse

import tornado.httpserver
import tornado.ioloop
import tornado.iostream
import tornado.web
import tornado.httpclient


class ProxyHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST']

    @tornado.web.asynchronous
    def get(self):

        def handle_response(response):
            if response.error and not isinstance(
                response.error, tornado.httpclient.HTTPError
            ):
                self.set_status(500)
                self.write('Internal server error:\n' + str(response.error))
                self.finish()
            else:
                self.set_status(response.code)
                for k, v in response.headers.items():
                    self.set_header(k, v)
                # If redirect, then redirect
                if hasattr(response, "effective_url"):
                    port_uri = getattr(response, "effective_url").replace(
                        "http://localhost:", "")
                    port, uri = port_uri.split(
                        "/")[0], "/".join(port_uri.split("/")[1:])
                    url = "http://{}:{}/{}".format(host, port, uri)
                    self.redirect(url)
                if response.body:
                    self.write(response.body)
                self.finish()

        # Get hostname, and then pick which port we need from map
        host = self.request.host.split(":")[0]
        if host not in vhost_map:
            return  # Don't even respond to the request
        port = random.choice(vhost_map[host])

        req = tornado.httpclient.HTTPRequest(
            url="http://localhost:{}{}".format(port, self.request.uri),
            method=self.request.method, body=self.request.body,
            headers=self.request.headers, follow_redirects=False,
            allow_nonstandard_methods=True
        )

        client = tornado.httpclient.AsyncHTTPClient()
        try:
            client.fetch(req, handle_response)
        except tornado.httpclient.HTTPError as e:
            if hasattr(e, 'response') and e.response:
                handle_response(e.response)
            else:
                self.set_status(500)
                self.write('Internal server error:\n' + str(e))
                self.finish()

    @tornado.web.asynchronous
    def post(self):
        return self.get()


def run_proxy(port, start_ioloop=True):
    """
    Run proxy on the specified port. If start_ioloop is True (default),
    the tornado IOLoop will be started immediately.
    """
    app = tornado.web.Application([
        (r'.*', ProxyHandler),
    ])
    app.listen(port)
    ioloop = tornado.ioloop.IOLoop.instance()
    if start_ioloop:
        ioloop.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Tornado-based proxy server matching hostname"
        " to ports."
    )
    parser.add_argument(
        '-p', '--port', type=int, help="Port to listen on.",
        default=8888, dest="port")
    parser.add_argument(
        '-v', '--vhost-map', type=str, default="vhost_map.json",
        help="Path to JSON file which contains mapping for hostname"
        " to port list", dest="vhost_map"
    )
    args = parser.parse_args()

    port = args.port
    vhost_map = json.load(open(args.vhost_map, "r"))

    print("Starting HTTP proxy on port %d" % port)
    run_proxy(port)
