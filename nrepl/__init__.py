#!/usr/bin/env python

import socket, re, sys
import nrepl.bencode as bencode
import threading
try:
    from urlparse import urlparse, ParseResult
except ImportError:
    from urllib.parse import urlparse, ParseResult

def _bencode_connect (uri):
    s = socket.create_connection(uri.netloc.split(":"))
    # TODO I don't think .close() will propagate to the socket automatically...
    f = s.makefile('rw')
    return bencode.BencodeIO(f)

def _match_criteria (criteria, msg):
    for k, v in criteria.items():
        mv = msg.get(k, None)
        if isinstance(v, set):
            if mv not in v:
                return False
        elif not v and mv:
            pass
        elif not mv or v != mv:
            return False
    return True

class WatchableConnection (object):
    def __init__ (self, IO):
        """Create a new WatchableConnection with an nREPL message transport
        supporting `read()` and `write()` methods that return and accept nREPL
        messages, e.g. bencode.BencodeIO."""
        self._IO = IO
        self._watches = {}
        class Monitor (threading.Thread):
            def run (_):
                for incoming in self._IO:
                    # Dirty hack so we can iterate over the list.
                    # RuntimeError: dictionary changed size during iteration (Python3)
                    # So we just force out an iteration, even tho we get errors.
                    # Better approach is wanted, but all tests are passing, so yeah.
                    while True:
                        try:
                            for key, (pred, callback) in self._watches.items():
                                if pred(incoming): 
                                    callback(incoming, self, key)
                        except RuntimeError as e:
                            pass
                        finally:
                            break

        self._thread = Monitor()
        self._thread.daemon = True
        self._thread.start()

    def close (self):
        self._IO.close()

    def send (self, message):
        "Send an nREPL message."
        self._IO.write(message)

    def unwatch (self, key):
        "Removes the watch previously registered with [key]."
        self._watches.pop(key, None)

    def watch (self, key, criteria, callback):
        """Registers a new watch under [key] (which can be used with `unwatch()`
        to remove the watch) that filters messages using [criteria] (may be a
        predicate or a 'criteria dict' [see the README for more info there]).
        Matching messages are passed to [callback], which must accept three
        arguments: the matched incoming message, this instance of
        `WatchableConnection`, and the key under which the watch was
        registered."""
        if hasattr(criteria, '__call__'):
            pred = criteria
        else:
            pred = lambda incoming: _match_criteria(criteria, incoming) 
        self._watches[key] = (pred, callback)

# others can add in implementations here
_connect_fns = {"nrepl": _bencode_connect}

def connect (uri):
    """Connects to an nREPL endpoint identified by the given URL/URI.  Valid
    examples include:

      nrepl://192.168.0.12:7889
      telnet://localhost:5000
      http://your-app-name.heroku.com/repl

    This fn delegates to another looked up in  that dispatches on the scheme of
    the URI provided (which can be a string or java.net.URI).  By default, only
    `nrepl` (corresponding to using the default bencode transport) is supported.
    Alternative implementations may add support for other schemes, such as
    http/https, JMX, various message queues, etc."""
    #
    uri = uri if isinstance(uri, ParseResult) else urlparse(uri)
    if not uri.scheme:
        raise ValueError("uri has no scheme: " + uri)
    f = _connect_fns.get(uri.scheme.lower(), None)
    if not f:
        raise Exception("No connect function registered for scheme `%s`" % uri.scheme)
    return f(uri)

