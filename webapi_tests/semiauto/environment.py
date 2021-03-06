#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import threading

from server import FrontendServer

from tornado.ioloop import IOLoop


"""Used to hold a TestEnvironment in a static field."""
env = None


def get(environ, *args, **kwargs):
    global env
    if not env:
        env = environ(*args, **kwargs)
        env.start()
    assert env.is_alive()
    return env


class InProcessTestEnvironment(object):
    def __init__(self, addr=("localhost", 6666), server_cls=None,
                 io_loop=None, verbose=False):
        self.addr = addr
        self.io_loop = io_loop or IOLoop()
        self.started = False
        self.handler = None

        if server_cls is None:
            server_cls = FrontendServer
        self.server = server_cls(addr, io_loop=self.io_loop,
                                 verbose=verbose)

    def start(self, block=False):
        """Start the test environment.

        :param block: True to run the server on the current thread,
            blocking, False to run on a separate thread.

        """

        self.started = True

        if block:
            self.server.start()
        else:
            self.server_thread = threading.Thread(target=self.server.start)
            self.server_thread.daemon = True  # don't hang on exit
            self.server_thread.start()

    def stop(self):
        """Stop the test environment.

        If the test environment is not running, this method has no effect.

        """

        if self.started:
            try:
                self.server.stop()
                self.server_thread.join()
                self.server_thread = None
            except AttributeError:
                pass
            self.started = False
        self.server = None

    def is_alive(self):
        return self.started


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    env = InProcessTestEnvironment()
    print("Listening on %s" % ":".join(str(i) for i in env.server.addr))
    # We ask the environment to block here so that the program won't
    # end immediately.
    env.start(block=True)
