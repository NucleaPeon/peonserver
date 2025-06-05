==========
PeonServer
==========

Introduction
============

PeonServer is a fast daemonized web server written in Python based on Tornado.

Features of PeonServer include:

    [X] Built-in sass compilation
    [X] Optional API method validation via FormEncode
    [X] Run daemonized or in a process
    [X] Virtual Environment compatible
    
Installation
============

Virtual Environment
-------------------

While your preference of virtual environment may differ, I use ``direnv`` which enables virtual environments based on the directory you are in.

My .envrc file:

```
layout python python3.11
```

Ensure the direnv hook is in your ``.bashrc`` file and run ``direnv allow``

https://direnv.net/docs/hook.html


Everything Else
---------------

```
git clone https://github.com/NucleaPeon/peonserver.git
cd peonserver
pip install -r requirements.txt -e .
```


Usage
=====

Start as a Process
------------------

```
python -m peonserver --no-daemon
```



