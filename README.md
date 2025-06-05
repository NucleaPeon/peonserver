PeonServer
==========

Introduction
------------

PeonServer is a fast daemonized web server written in Python based on Tornado.

Features of PeonServer include:

    [X] Run daemonized or in a process
    [X] Asynchronous
    [X] Built-in sass compilation
    [X] Optional API method validation via FormEncode
    [X] Optional separation of website code and server
    [X] Virtual Environment compatible
    
Installation
------------

### Virtual Environment


While your preference of virtual environment may differ, I use ``direnv`` which enables virtual environments based on the directory you are in.

My .envrc file:

```
layout python python3.11
```

Ensure the direnv hook is in your ``.bashrc`` file and run ``direnv allow``

https://direnv.net/docs/hook.html


### Everything Else

```
git clone https://github.com/NucleaPeon/peonserver.git
cd peonserver
pip install -r requirements.txt -e .
```

### Post Installation

Since we utilize files that contain keys and secrets, this is something that no one wants to accidentally commit to their repo.
I want the file to exist when people check out the repo, but not allow changes to be committed.

  - `.gitignore` will track changes if file is added even if it's ignored after
  - `git update-index --skip-worktree <filepath>` is useful but requires users to run it and if there are changes to upstream, users may overlook updates to the README file.
  - Lastly, there are git hooks but these cannot be committed to a repo.

Sufficed to say, I am going with the git hook route, but with a twist. It does require you to manually run this command after checkout:

```
git config --local core.hooksPath githooks/
```

For every additional ignore file, a simple ``git pull`` will automatically include changes and prevent sensitive data being committed.


Server Usage
------------

### Start as a Process

```
python -m peonserver --no-daemon
```

### Start as a Daemon

```
python -m peonserver start
```

Check its status:

```
python -m peonserver status
```


### Useful Options

``--debug`` will increase verbosity and will autoreload when scss/sass/js/css files or the ``/static/index.html`` file is modified.

Building Websites
-----------------

PeonServer is capable of developing webpages right off the bat, but it also allows developers to isolate their web code from the server code.

Run the script to create the website:

``./create-website``

and then modify the underlying ``website/static/...`` contents in the same way you would using the basic peonserver setup.
The ``website`` directory is under ``.gitignore`` so it's something you should manage yourself. Turn it into its own git repo and then push and pull website-only changes there.

In this manner, it'll be easier to port to and from peonserver to other web servers, unless you utilize tornado-specific templating/static variable referencing within html code.

