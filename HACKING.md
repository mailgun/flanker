Hacking
=======

### Installing

See the [Quickstart Guide](README.md) for instructions on how to install Flanker.

### Running Tests

Call `nosetests` in the `tests` directory to run unit tests. Note, some (network based) tests use `mock`.

```bash
$ cd ~/flanker/tests
$ nosetests
S..S..S..S..S..S.............................................SS................................................................................................................................................................
----------------------------------------------------------------------
Ran 223 tests in 2.256s

OK (SKIP=8)
````

Call with `--no-skip` to run all tests.

```bash
$ cd ~/flanker/tests
$ nosetests --no-skip
...............................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 223 tests in 7.806s

OK
```

### Discussion

Please use GitHub issues to discuss bugs, feature requests, and any other issues you may have with Flanker.

### Code Style Guidelines

Try to stick as close as possible to PEP8.

### Sending Pull Requests

Please ensure that any changes you make to Flanker are covered by tests.
