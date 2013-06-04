import os, unittest, subprocess, re, signal, time
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
        # neither os.kill, self.proc.kill, or self.proc.terminate were shutting
        # down the leiningen/clojure/nrepl process(es)
        c = nrepl.connect("nrepl://localhost:" + self.port)
        c.write({"op": "eval", "code": "(System/exit 0)"})

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
        outs = {}
        def add_resp (session, msg):
            out = msg.get("out", None)
            if out: outs[session].append(out)
        def watch_new_sessions (msg, wc, key):
            session = msg.get("new-session")
            outs[session] = []
            wc.watch("session" + session, {"session": session},
                    lambda msg, wc, key: add_resp(session, msg))
        wc.watch("sessions", {"new-session": None}, watch_new_sessions)
        wc.send({"op": "clone"})
        wc.send({"op": "clone"})
        time.sleep(0.5)
        for i, session in enumerate(outs.keys()):
            wc.send({"op": "eval",
                "session": session,
                "code": """(do (future (Thread/sleep %s00)
                (println %s)
                (println (System/currentTimeMillis))))""" % (i, i)})
        time.sleep(1)
        for i, (session, _outs) in enumerate(outs.items()):
            self.assertEqual(i, int(_outs[0]))
        self.assertTrue(int(outs.values()[0][1]) < int(outs.values()[1][1]))


if __name__ == '__main__':
    unittest.main()

