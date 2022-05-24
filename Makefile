VERSION="0.0.20"

clean:
	rm -rf build dist papr.egg-info

build: clean
	python3 setup.py sdist bdist_wheel
	
install: clean
	pip3 uninstall -y papr
	python3 setup.py sdist bdist_wheel
	pip3 install --user dist/*.whl

dockerimage:
	docker build -t papr/1 -f docker/Dockerfile .

dockerimage-nocache:
	docker build --no-cache -t papr/1 -f docker/Dockerfile .

runimage:
	docker run --dns=8.8.8.8 -t -i -e DISPLAY=${DISPLAY} -v ${PWD}:/host/ -v /tmp/.X11-unix:/tmp/.X11-unix -v /dev/shm:/dev/shm --rm papr/1

reinstall: clean build
	pip3 install --user --no-deps --force-reinstall dist/papr-$(VERSION)-py3-none-any.whl

indocker:
	docker run -t -i -e DISPLAY=${DISPLAY} -v ${PWD}/papr:/root/papr/papr -v ${PWD}/scripts:/root/papr/scripts -v /tmp/.X11-unix:/tmp/.X11-unix -v /dev/shm:/dev/shm --rm papr/1
