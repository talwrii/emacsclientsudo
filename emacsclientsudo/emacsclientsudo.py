#!/usr/bin/python3

import asyncio
import argparse
import logging
import os
import contextlib
import sexpdata

BAD_FUNCTIONS = ['apply', 'funcall']
ALWAYS_LEGAL_FUNCTIONS = ['list']

LOGGER = logging.getLogger()

PARSER = argparse.ArgumentParser(description='Filter emacsclient commands')
PARSER.add_argument('--debug', action='store_true', help='Print debug output')
PARSER.add_argument('listen', type=str, help='Unix domain socket to listen on')
PARSER.add_argument('connect', type=str, help='Unix domain socket to connect to')
PARSER.add_argument(
    '--allow-function',
    action='append',
    type=str,
    help='Allow this function to be executed',
    dest='legal_functions')
args = PARSER.parse_args()

def parse_request(line):
    return line.split(' ')

def get_expressions(line):
    start = 0
    while True:
        try:
            start = line.index('-eval', start) + 1
        except ValueError:
            # No more evals
            break
        yield parse_expression(line[start])


def request_allowed(line, legal_functions):
    # I think we can allow tty because this allow process writing onto our tty that
    #    that we don't control, eval is only dangerous thing.

    # One dangerous break out comes from compilation / execution within emacs...
    #   but using emacs is too convenient... Just don't run code.
    try:
        if '-eval' in line:
            expressions = list(get_expressions(line))
            return all(expression_allowed(exp, legal_functions) for exp in expressions)
        else:
            return True
    except:
        LOGGER.exception('Failed to understanding request (%r) blocking', line)
        return False

def parse_expression(exp):
    result, = sexpdata.parse(exp.replace('&_', ' ')) # Wrapping
    return result

def expression_allowed(exp, legal_functions):
    calls = get_function_calls(exp)
    illegal_calls = [f for f in calls if f not in legal_functions]
    LOGGER.debug('Illegal function calls in expression %r', illegal_calls)
    return not bool(illegal_calls)

def get_function_calls(exp):
    if not isinstance(exp, list):
        return []
    else:
        return get_function_name(exp[0]) + sum(map(get_function_calls, exp[1:]), [])

def get_function_name(thing):
    if isinstance(thing, (int, float)):
        return []
    elif isinstance(thing, sexpdata.Symbol):
        return [thing.value()]
    else:
        raise ValueError(thing)

class Server(object):
    def __init__(self, server_file, legal_functions):
        self.server_file = server_file
        self.legal_functions = legal_functions

    async def new_connection(self, client_reader, client_writer):
        LOGGER.debug('New connection')
        line = await client_reader.readline()
        line = line.decode('utf8')
        LOGGER.debug('Got command %r', line)
        request = parse_request(line)
        if request_allowed(request, self.legal_functions):
            server_reader, server_writer = await asyncio.open_unix_connection(self.server_file)
            LOGGER.debug('Forwarding command')
            server_writer.write((line).encode('utf8'))
            LOGGER.debug('Waiting for response')
            response = await server_reader.read()
            LOGGER.debug('Got response %r', response)
            client_writer.write(response)
            client_writer.close()
        else:
            LOGGER.error('Refusing to forward request %r', request)
            error = '-emacs-pid {}\n-error Authorization&_failed:emacsclientproxy&_blocked_&command'.format(os.getpid())
            client_writer.write(error.encode('utf8'))
            client_writer.close()

def main():
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    legal_functions = args.legal_functions or []

    bad_legal_functions = [x for x in legal_functions if x in BAD_FUNCTIONS]
    if bad_legal_functions:
        raise Exception('Allowing these functions will break sandboxing: %r', bad_legal_functions)

    legal_functions += ALWAYS_LEGAL_FUNCTIONS
    legal_functions.sort()

    LOGGER.debug('Allowing these functions %r', legal_functions)
    server = Server(args.connect, legal_functions)
    run_server = asyncio.start_unix_server(
        client_connected_cb=server.new_connection,
        path=args.listen)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_server)
    loop.run_forever()
