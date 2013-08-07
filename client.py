import cmd
import json
import requests


class RestShell(cmd.Cmd):
    intro = "Welcome to the RESTful Shell"
    prompt = "(shell) "

    def emptyline(self):
        pass

    def default(self, line):
        endpoint = "http://localhost:8080/execute"

        payload = {
            'command': line,
        }

        headers = {
            'Content-Type': 'application/json',
        }

        response = requests.post(endpoint,
                                 data=json.dumps(payload),
                                 headers=headers)
        data = response.json()
        print data.get('output', "")

    def do_EOF(self, line):
        return True

    def do_exit(self, line):
        return True


if __name__ == '__main__':
    RestShell().cmdloop()
