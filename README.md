[WIP] Remote VirtualBox
-----------------------

## About

This package is intended to be simple and useful abstraction based on [Zeep](https://github.com/mvantellingen/python-zeep) SOAP client.

It doesn't depend on ancient VirtualBox Python SDK and even more ancient ZSI (last updated in 2006) and PyXML (thing from 2007) libraries.

The initial goal was to build an easy to use [CuckooSandbox](https://github.com/cuckoosandbox/cuckoo) machinery.

## VirtualBox Webservice

There is an official manual how to start it:

https://www.virtualbox.org/manual/ch09.html#vboxwebsrv-daemon

## Install

```
pip install remotevbox --user
```

### Development version

[Pipenv](https://github.com/kennethreitz/pipenv) is used here:

```
pipenv install
```

## Usage example

```python
    >>> import remotevbox
    >>> vbox = remotevbox.connect("https://127.0.0.1:18083", "vbox", "yourpassphrase")
    >>> vbox.get_version()
    '5.1.30'
    >>> machine = vbox.get_machine("Windows10")
    >>> machine.launch()
    >>> machine.save()
    >>> vbox.disconnect()
```
