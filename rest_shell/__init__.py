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
import json
import subprocess
import sys
import tempfile

import bottle
import requests


@bottle.route('/execute', method='POST')
def execute():
    """ Execute supplied command and return response """
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
    print host, port

    bottle.run(host=host, port=port)


class RestShellClient(cmd.Cmd):
    """ Command shell implementation for RESTful Shell API """
    intro = "Welcome to the RESTful shell!"
    location = ""

    def remote_execute(self, command):
        """ Send HTTP request to API and return output """
        endpoint = "http://%s/execute" % self.location
        payload = {'command': command}
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(endpoint,
                                     data=json.dumps(payload),
                                     headers=headers)
            data = response.json()
        except requests.exceptions.ConnectionError, err:
            print err
            sys.exit(1)

        return data.get('output', "")

    def preloop(self):
        user = self.remote_execute('whoami').strip()
        self.prompt = "(http://%s@%s) " % (user, self.location)

    def emptyline(self):
        pass

    def default(self, line):
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
