#!/usr/bin/env python
#
# HTTP Proxy Server for Proxying to Local Virtual Hosts
#
# GET/POST proxying based on
# http://groups.google.com/group/python-tornado/msg/7bea08e7a049cf26
#
# Copyright (C) 2012 Senko Rasic <senko.rasic@dobarkod.hr>
# Copyright (C) 2014 Hamza Faran <hamza@hfaran.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import random
import json
import argparse

import tornado.httpserver
import tornado.ioloop
import tornado.iostream
import tornado.web
import tornado.httpclient

__all__ = ['ProxyHandler', 'run_proxy']


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
                    self.redirect(getattr(response, "effective_url"))
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
