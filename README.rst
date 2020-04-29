==========
guppywuppy
==========


.. image:: https://img.shields.io/pypi/v/guppywuppy.svg
        :target: https://pypi.python.org/pypi/guppywuppy

.. image:: https://img.shields.io/travis/peterk87/guppywuppy.svg
        :target: https://travis-ci.com/peterk87/guppywuppy

.. image:: https://readthedocs.org/projects/guppywuppy/badge/?version=latest
        :target: https://guppywuppy.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Service wrapping Oxford Nanopore PyGuppyClient_


* Free software: MIT license
* Documentation: https://guppywuppy.readthedocs.io.


Features
--------

* pulls FAST5 files from a fast5watch_ server running on a machine running MinKNOW
* sends FAST5 files to a `guppy_basecall_server` for real-time GPU accelerated basecalling  
* saves FASTQ files in a similar format to `guppy_basecaller`
* compatible with Rampart_ analysis and visualization

Known Issues
------------

zmq.error.ZMQError: Too many open files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`ulimit -n` may be set really low (e.g. 1024) and needs to be set higher for ZMQ to be able to open a large number of sockets (see issue https://github.com/zeromq/jeromq/issues/183) 



Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _fast5watch: https://github.com/peterk87/fast5watch
.. _PyGuppyClient: https://github.com/nanoporetech/pyguppyclient/
.. _Rampart: https://github.com/artic-network/rampart/
