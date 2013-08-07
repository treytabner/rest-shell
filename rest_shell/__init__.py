"""
The RESTful Shell

This is a RESTful shell that gives you command line access to a server that
does not provide another means of shell access.  If you are limited to an API
to interact with your server, this tool may work for you.

"""

# The RESTful Shell
# Copyright (c) 2013 Trey Tabner <trey@tabner.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import cmd
import os
import simplejson
import subprocess
import sys
import tempfile

import bottle
import requests


@bottle.route('/execute', method='POST')
def execute():
    """ Execute supplied command and return response """
    apikey = bottle.request.headers.get('X-Auth-Token')
    if apikey != os.environ.get('TOKEN'):
        # Bail if the token doesn't match
        bottle.abort(code=401, text="TOKEN environment variable doesn't match")

    command = bottle.request.json.get('command')

    if not command:
        bottle.abort(code=400)

    with tempfile.TemporaryFile() as stdout:
        status = subprocess.call(command,
                                 shell=True,
                                 stdout=stdout,
                                 stderr=subprocess.STDOUT)
        stdout.seek(0)
        output = stdout.read()

    response = {
        'status': status,
        'output': output,
    }

    return response


def run(location):
    """ Run the web server with Python bottle """
    (host, port) = location.split(':')

    if not os.environ.get('TOKEN'):
        print "WARNING! No TOKEN specified, running without authentication"

    bottle.run(host=host, port=port)


class RestShellClient(cmd.Cmd):
    """ Command shell implementation for RESTful Shell API """
    intro = "Welcome to the RESTful shell!"
    location = ""

    def remote_execute(self, command):
        """ Send HTTP request to API and return output """
        endpoint = "http://%s/execute" % self.location
        payload = {'command': command}
        headers = {
            'Content-Type': 'application/json',
            'X-Auth-Token': os.environ.get('TOKEN'),
        }

        try:
            response = requests.post(endpoint,
                                     data=simplejson.dumps(payload),
                                     headers=headers)
        except requests.exceptions.ConnectionError, err:
            print err
            sys.exit(1)

        if response.status_code == 200:
            data = response.json()
            return data.get('output', "")
        elif response.status_code == 401:
            print "Authentication failed, do you have TOKEN set properly?"
            sys.exit(1)

    def preloop(self):
        """ Setup the prompt """

        user = self.remote_execute('whoami')
        self.prompt = "(http://%s@%s) " % (user.strip(), self.location)

    def emptyline(self):
        """ Ignore empty lines """
        pass

    def default(self, line):
        """ Remotely execute command """
        print self.remote_execute(line).strip()

    @staticmethod
    def do_EOF(line):  # pylint: disable=C0103,W0613
        """ Handle EOF in the shell """
        return True

    @staticmethod
    def do_exit(line):  # pylint: disable=C0103,W0613
        """ Handle exit command in the shell """
        return True


def main():
    """ Parse arguments and run either the server or client """
    parser = argparse.ArgumentParser(description="Start a RESTful shell")
    parser.add_argument('--server', action='store_true',
                        help="Launch server instead of client")
    parser.add_argument('location', help="Use specified endpoint, "
                                         "example: localhost:8080")
    args = parser.parse_args()

    if args.server:
        run(args.location)
    else:
        client = RestShellClient()
        client.location = args.location
        try:
            client.cmdloop()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
