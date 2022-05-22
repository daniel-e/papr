# Test migration of storage structure from 0.0.18 to 0.0.19 

From version 0.0.18 to 0.0.19 the storage structure has changed. Instead of storing the
summary and notes in the sqlite3 database, the data is stored in notes.md and summary.md
in the new directory `data` in a repository.

Steps to test the migration:

* install papr 0.0.18
* create a repository with `papr init`
* download some papers
* create notes and summaries
* install papr 0.0.19
* when starting the new version you should see a message that you have to upgrade
* run `papr migrate`
* run papr again - now it should start without the message
* verify that notes and summaries are still available
* verify the files on disc
  * repo/.paper/meta.yml should exist with version 2
  * repo/data/p... should exist with notes and summaries
* edit notes and summaries
* verify that changes are persisted

# Publish a new version to PyPI

- [x] Set a new version in setup.py
- [x] Set a new version in config.py::_PAPR_VERSION
- [x] Set a new version in Makefile (section reinstall)
- [x] Update ChangeLog
- [x] Update new feature description in ui.py::show_new_features
- [x] commit everything into branch + push
- [ ] merge branch into master
  - git checkout master
  - git merge v0.0.??
  - git push (to master)
- [ ] create screenshot
- [ ] make clean
- [ ] make build
- [ ] python3 -m pip install --user --upgrade twine
- [ ] test.pypi.org
  - twine upload --repository-url https://test.pypi.org/legacy/ dist/*
  - enter username and password for test.pypi.org
  - check https://test.pypi.org/project/papr/
- [ ] live
  - twine upload dist/*
  - check that you can install it
    make runimage
    python3 -m pip uninstall papr
    python3 -m pip install --no-cache-dir papr
- [ ] give it a tag, e.g. "v0.0.13" (git tag -a v0.0.13 -m comment)
- [ ] push it (git push --tags)
- [ ] test: pip3 install papr
- [ ] announce
  - use monospace font for "pip3 install papr" from https://yaytext.com/monospace/
    𝚙𝚒𝚙3 𝚒𝚗𝚜𝚝𝚊𝚕𝚕 𝚙𝚊𝚙𝚛 <- this should be UTF-8 chars monospaced
- [ ] branch for next version: git checkout -b v0.0.18

Example:
Released version 0.0.18 of papr - a simple command line tool to manage scientific papers. New: create summaries, context menu, hide papers, change title, new version notification. [pip3 install papr] [screenshot] https://github.com/daniel-e/papr





Use Case: As a user I want to play around with papr
===================================================

You can use the docker environment for those things as you can create
repositories and delete repositories without the risk that you play with your
repositories on your machine:

    xhost +
    # If `make dockerimage` doesn't work try `make dockerimage-nocache`.
    make dockerimage
    make runimage

In `/root/example/small_repo` you can find a small repository which you can
use for testing:

    cd example/small_repo
    papr


Testing
=======

    make dockerimage
    make runimage
    cd /host
    make reinstall




Use Case: As a developer I want to use the latest scripts from the host
=======================================================================

Instead of running

    xhost +
    make preparedocker
    make indocker 




# Install from local

    pip3 uninstall -y papr
    rm -rf build dist papr.egg-info
    python3 setup.py sdist bdist_wheel
    pip3 install --user dist/*.whl
    rm -rf build dist papr.egg-info

or simply run:

    make install

# Test

This command uses `cli.py` from the `papr` directory to build a new repository in `/tmp/repo`. 

    make preparedocker
    make runtest
    
# Userful link

It's very useful to have symbolic link to `papr/cli.py`. I'm using `~/bin/papr.py` which points to the dev version of `cli.py`.



# pip

From https://packaging.python.org/tutorials/packaging-projects/

Make sure you have the latest versions of setuptools and wheel installed:

    python3 -m pip install --user --upgrade setuptools wheel

Now run this command from the same directory where setup.py is located:

    python3 setup.py sdist bdist_wheel

https://test.pypi.org/
# twine is used to upload packages
python3 -m pip install --user --upgrade twine

# upload
# need user + pw for test instance
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# View project
https://test.pypi.org/project/papr/
# Install from test instance
python3 -m pip install --index-url https://test.pypi.org/simple/ papr


-------------------------------------------------------------------------------


# create package
rm -rf build dist
python3 setup.py sdist bdist_wheel
# upload
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# uninstall local version
python3 -m pip uninstall papr
# Delete version on pypi
# install
python3 -m pip install --no-cache-dir --index-url https://test.pypi.org/simple/ papr


---------------
LIVE

twine upload dist/*
python3 -m pip install --no-cache-dir papr


----------------


