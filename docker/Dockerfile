FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get -y install apt-utils aptitude git curl net-tools iputils-ping tcpdump
RUN apt-get -y install python3 python3-pip virtualenv
RUN apt-get -y install jq evince vim

RUN pip3 install bs4 termcolor markdown


RUN echo "alias ..='cd ..'" >> ~/.bashrc
RUN echo "alias l='ls -l'" >> ~/.bashrc

ADD papr /tmp/papr/papr
ADD scripts /tmp/papr/scripts
ADD setup.py /tmp/papr/
ADD README.md /tmp/papr/

# Initialize demo repository.
ADD docker/example /root/example
RUN mkdir -p /root/.papr
RUN echo '{"cfg_version": "0.0.1", "default_repo": "/root/example/small_repo"}' > /root/.papr/papr.cfg

ENV PATH=/root/.local/bin/:${PATH}
ENV LANG=C.UTF-8

WORKDIR /tmp/papr/
RUN python3 setup.py sdist bdist_wheel
RUN pip3 install --user dist/*.whl

WORKDIR /root
CMD ["/bin/bash"]
