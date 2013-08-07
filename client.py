import argparse
import cmd
import json
import requests
import sys
import urlparse


class RestShell(cmd.Cmd):
    intro = "Welcome to the RESTful shell!"

    def remote_execute(self, command):
        endpoint = "%s/execute" % self.args.URL
        payload = {'command': command}
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(endpoint,
                                     data=json.dumps(payload),
                                     headers=headers)
            data = response.json()
        except requests.exceptions.ConnectionError, e:
            print e
            sys.exit(1)

        return data.get('output', "")

    def preloop(self):
        parser = argparse.ArgumentParser(description="Start a RESTful shell")
        parser.add_argument('URL', help="Use specified URL for endpoint")

        self.args = parser.parse_args()

        user = self.remote_execute('whoami').strip()
        url = urlparse.urlparse(self.args.URL)

        self.prompt = "(%s://%s@%s) " % (url.scheme, user, url.netloc)

    def emptyline(self):
        pass

    def default(self, line):
        print self.remote_execute(line).strip()

    def do_EOF(self, line):
        return True

    def do_exit(self, line):
        return True


def main():
    try:
        RestShell().cmdloop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
