import argparse
import bottle
import shlex
import subprocess
import tempfile


@bottle.route('/execute', method='POST')
def execute():
    """ Execute supplied command and return response """
    command = bottle.request.json.get('command')

    if not command:
        bottle.abort(code=400)

    args = shlex.split(command)

    with tempfile.TemporaryFile() as stdout:
        try:
            status = subprocess.call(args, stdout=stdout, stderr=subprocess.STDOUT)
            stdout.seek(0)
            output = stdout.read()
        except Exception, e:
            status = -1
            output = str(e)

    response = {
        'status': status,
        'output': output,
    }

    return response


if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(host='localhost', port=8080, reloader=True)
