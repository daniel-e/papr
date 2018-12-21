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

rm -rf build dist && python3 setup.py sdist bdist_wheel && pip3 install dist/*.whl

