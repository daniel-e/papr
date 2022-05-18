FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get -y install apt-utils aptitude git curl net-tools iputils-ping tcpdump
RUN apt-get -y install python3 python3-pip virtualenv
RUN apt-get -y install jq evince vim
RUN apt-get -y install firefox

RUN pip3 install bs4 termcolor markdown

RUN adduser --disabled-password --gecos "" dz
USER dz

ADD papr /tmp/papr/papr
ADD scripts /tmp/papr/scripts
ADD setup.py /tmp/papr/
ADD README.md /tmp/papr/

RUN echo "alias ..='cd ..'" >> ~/.bashrc
RUN echo "alias l='ls -l'" >> ~/.bashrc

ENV HOME=/home/dz

# Initialize demo repository.
ADD docker/example $HOME/example
RUN mkdir -p $HOME/.papr
RUN echo '{"cfg_version": "0.0.1", "default_repo": "/home/dz/example/small_repo"}' > $HOME/.papr/papr.cfg

ENV PATH=$HOME/.local/bin/:${PATH}
ENV LANG=C.UTF-8

WORKDIR /tmp/papr/

USER root
RUN chown -R dz:dz /home/dz
RUN chown -R dz:dz .
USER dz

RUN python3 setup.py sdist bdist_wheel
RUN pip3 install --user dist/*.whl

WORKDIR /host

CMD ["/bin/bash"]
