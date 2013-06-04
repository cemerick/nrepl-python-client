
import socket, re, sys
from urlparse import urlparse, ParseResult
import nrepl.bencode as bencode
import threading

def responses (transport, timeout=sys.float_info.max):
    """A generator that produces messages received on the given transport.
    Will block up to [timeout] seconds (a float).  The generator will
    terminate only when the underlying transport is closed, or if a message
    takes longer than [timeout] seconds to arrive."""
    while True:
        x = transport.recv(timeout)
        if not x: break
        yield x

# def client (transport, timeout):
#    """Returns a fn of zero and one argument, both of which return the current head of a single
#    response-seq being read off of the given client-side transport.  The one-arg arity will
#    send a given message on the transport before returning the seq.
# 
#    Most REPL interactions are best performed via `message` and `client-session` on top of
#    a client fn returned from here."""
#    head = None
#    def restart ():
#        return head = responses(transport, timeout)
#    def client_fn (message=None):
#        if message: transport.send(message)
#        return restart()

def socket_connect (host, port, transport_fn):
    transport_fn(socket.create_connection((host, port)))

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
        elif m != mv:
            return False
    return True

class WatchableConnection (object):
    def __init__ (self, IO):
        self._IO = IO
        self._watches = {}
        class Monitor (threading.Thread):
            def run (_):
                for incoming in self._IO:
                    for key, (pred, callback) in self._watches:
                        if pred(incoming): callback(incoming, self, key)
        self._thread = Monitor()
        self._thread.daemon = True
        self._thread.start()

    def close (self):
        self._IO.close()

    def send (self, message):
        self._IO.write(message)

    def unwatch (self, key):
        self._watches.pop(key, None)

    def watch (self, key, criteria, callback):
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

    This fn delegates to another looked up in  that dispatches on the scheme of the URI provided
    (which can be a string or java.net.URI).  By default, implementations for
    nrepl (corresponding to using the default bencode transport) and
    http/https (using the drawbridge-compatible transport in nrepl.http) are
    registered.  Alternative implementations may add support for other schemes,
    such as JMX, various message queues, etc."""
    #
    uri = uri if isinstance(uri, ParseResult) else urlparse(uri)
    if not uri.scheme:
        raise ValueError("uri has no scheme: " + uri)
    f = _connect_fns.get(uri.scheme.lower(), None)
    if not f:
        raise Exception("No connect function registered for scheme `%s`" % uri.scheme)
    return f(uri)

