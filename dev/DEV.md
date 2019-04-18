# Use Case: As a user I want to play around with papr.

You should use the docker environment for those things as you can create
repositories and delete repositories without the risk that you play with your
real repositories on your machine:

    xhost +
    make preparedocker
    make runtest

In the docker container there is a link from `/usr/bin/papr` which
points to the script in `/root/papr/papr/cli.py`.

Create a test repository:

    mkdir repo
    cd repo
    ../scripts/build_testrepo.sh

Now, you can just execute `papr`.

Note: if you modify the papr scripts on the host it has no effect on the
docker image.


# Use Case: As a developer I want to use the latest scripts from the host.

Instead of running

    make runtest
    
execute

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


