[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Filyaglow%2Fremote-virtualbox.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Filyaglow%2Fremote-virtualbox?ref=badge_shield)

[WIP] Remote VirtualBox
-----------------------

|Build Status|

About
-----

This package is intended to be simple and useful abstraction based on
`Zeep <https://github.com/mvantellingen/python-zeep>`__ SOAP client.

It doesn't depend on ancient VirtualBox Python SDK and even more ancient
ZSI (last updated in 2006) and PyXML (thing from 2007) libraries.

The initial goal was to build an easy to use
`CuckooSandbox <https://github.com/cuckoosandbox/cuckoo>`__ machinery.

VirtualBox Webservice
---------------------

There is an official manual how to start it:

https://www.virtualbox.org/manual/ch09.html#vboxwebsrv-daemon

Install
-------

::

    pip install remotevbox --user

Development version
~~~~~~~~~~~~~~~~~~~

`Pipenv <https://github.com/kennethreitz/pipenv>`__ is used here:

::

    pipenv install

Usage example
-------------

.. code:: python

        >>> import remotevbox
        >>> vbox = remotevbox.connect("https://127.0.0.1:18083", "vbox", "yourpassphrase")
        >>> vbox.get_version()
        '5.1.30'
        >>> machine = vbox.get_machine("Windows10")
        >>> machine.launch()
        >>> machine.save()
        >>> vbox.disconnect()

.. |Build Status| image:: https://travis-ci.org/ilyaglow/remote-virtualbox.svg?branch=master
   :target: https://travis-ci.org/ilyaglow/remote-virtualbox


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Filyaglow%2Fremote-virtualbox.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Filyaglow%2Fremote-virtualbox?ref=badge_large)