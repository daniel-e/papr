clean: 
	rm -rf build dist papr.egg-info

install: clean
	pip3 uninstall -y papr
	python3 setup.py sdist bdist_wheel
	pip3 install --user dist/*.whl
	rm -rf build dist papr.egg-info

newrepo:
	@./scripts/build_testrepo.sh
