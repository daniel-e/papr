FROM ubuntu:19.04

RUN apt-get update
RUN apt-get -y install apt-utils aptitude git curl net-tools iputils-ping tcpdump
RUN apt-get -y install python3 python3-pip virtualenv
RUN apt-get -y install jq
RUN apt-get -y install evince
RUN apt-get -y install vim

RUN pip3 install bs4 termcolor


RUN echo "alias ..='cd ..'" >> ~/.bashrc
RUN echo "alias l='ls -l'" >> ~/.bashrc

ADD papr /tmp/papr/papr
ADD scripts /tmp/papr/scripts
ADD setup.py /tmp/papr/
ADD README.md /tmp/papr/
ADD docker/example /root/example

ENV PATH=/root/.local/bin/:${PATH}
ENV LANG=C.UTF-8

WORKDIR /tmp/papr/
RUN python3 setup.py sdist bdist_wheel
RUN pip3 install --user dist/*.whl

WORKDIR /root
CMD ["/bin/bash"]
