# nrepl-python-client

Surprisingly, an [nREPL](http://github.com/clojure/tools.nrepl) client
written in Python.

It pretty much works.

Requires Python 2.7.  Will work with any nREPL >= 0.2.0 endpoint that uses the
default bencode socket transport.  Support for [other
transports](https://github.com/clojure/tools.nrepl/wiki/Extensions#transports)
should be straightforward, thanks to a unpythonic multimethod thing that
`nrepl.connect()` uses.

## Send help

* Patches / pull requests that contain good docs suitable for people that are
  likely to use this would be great.  There's not a lot of code, and some
  not-horrible tests, so usage shouldn't be too hard to figure out, but proper
  documentation would be nice.
* Make this a Proper Python Library.  I've been away from Python for a loooooong
  time, and I don't know what the current best practices are around eggs,
  distribution, and so on.  There's a stub of egg-info stuff here, but it's
  likely broken.
* Fix my busted Python.  Like I said, the last time I did any serious Pythoning
  was in the 2.3 days or something (to use new-style classes, or not, that was
  the question, etc).  If I goofed, open an issue with a fix.

## Need Help?

Ping `cemerick` on freenode irc or
[twitter](http://twitter.com/cemerick) if you have questions or would
like to contribute patches.

## License

Copyright ©2013 [Chas Emerick](http://cemerick.com) and other contributors

Distributed under the MIT License. Please see the `LICENSE` file at the top
level of this repo.
