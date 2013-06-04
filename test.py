import os, unittest, subprocess, re, signal
import nrepl
from nrepl.bencode import encode, decode

class BencodeTest (unittest.TestCase):
    def test_encoding (self):
        self.assertEqual('d1:ai1e1:cld1:xl1:yeee1:bli2eli3eeee',
                encode({"a": 1, "b": [2, [3]], "c": [{"x": ["y"]}]}))
        self.assertEqual([{u'a': 1, u'c': [{u'x': [u'y']}], u'b': [2, [3]]}],
                list(decode('d1:ai1e1:cld1:xl1:yeee1:bli2eli3eeee')))

class REPLTest (unittest.TestCase):
    def setUp (self):
        self.proc = subprocess.Popen(["lein", "repl", ":headless"],
                stdout=subprocess.PIPE)
        self.port = re.findall(r"\d+", self.proc.stdout.readline())[0]
        self.proc.stdout.close()

    def tearDown (self):
        # TODO neither of these actually kill the java proc hosting the REPL
        self.proc.kill()
        os.kill(self.proc.pid, signal.SIGKILL)

    def test_simple_connection (self):
        c = nrepl.connect("nrepl://localhost:" + self.port)
        c.write({"op": "clone"})
        r = c.read()
        self.assertEqual(["done"], r["status"])
        session = r["new-session"]
        self.assertIsNotNone(session)
        c.write({"op": "eval", "code": "(+ 1 2)", "session": session})
        r = c.read()
        self.assertEqual(session, r["session"])
        self.assertEqual("3", r["value"])
        self.assertEqual(["done"], c.read()["status"])
        c.write({"op": "eval", "code": "(+ *1 2)", "session": session})
        self.assertEqual("5", c.read()["value"])
        c.close()

    def test_async_watches (self):
        c = nrepl.connect("nrepl://localhost:" + self.port)
        wc = nrepl.WatchableConnection(c)
        rs = {}
        # TODO

if __name__ == '__main__':
    unittest.main()

