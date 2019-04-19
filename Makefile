clean: 
	rm -rf build dist papr.egg-info

install: clean
	pip3 uninstall -y papr
	python3 setup.py sdist bdist_wheel
	pip3 install --user dist/*.whl
	#rm -rf build dist papr.egg-info

newrepo:
	@./scripts/build_testrepo.sh

preparedocker:
	docker build --no-cache -t papr/1 .

runtest:
	docker run -t -i -e DISPLAY=${DISPLAY} -v ${PWD}:/host/ -v /tmp/.X11-unix:/tmp/.X11-unix -v /dev/shm:/dev/shm --rm papr/1

indocker:
	docker run -t -i -e DISPLAY=${DISPLAY} -v ${PWD}/papr:/root/papr/papr -v ${PWD}/scripts:/root/papr/scripts -v /tmp/.X11-unix:/tmp/.X11-unix -v /dev/shm:/dev/shm --rm papr/1
