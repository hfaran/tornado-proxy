#!/usr/bin/env python

from distutils.core import setup, Command
import os
import os.path


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        retval = os.system('python -m test')
        if retval != 0:
            raise Exception('tests failed')


setup(
    name='tornado-proxy',
    version='0.1.1',
    description='Simple asynchronous HTTP proxy',
    author='Senko Rasic, Hamza Faran',
    author_email='senko.rasic@dobarkod.hr, hamza@hfaran.com',
    cmdclass={
        # 'test': TestCommand  # TODO: Uncomment when tests added
    },
    packages=['tornado_proxy'],
)
