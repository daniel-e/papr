FROM ubuntu:18.10

RUN apt-get update
RUN apt-get -y install apt-utils aptitude git curl net-tools iputils-ping tcpdump
RUN apt-get -y install python3 python3-pip
RUN apt-get -y install jq
RUN apt-get -y install evince

RUN pip3 install bs4 termcolor


RUN echo "alias ..='cd ..'" >> ~/.bashrc
RUN echo "alias l='ls -l'" >> ~/.bashrc

ADD papr /root/papr/papr
ADD scripts /root/papr/scripts
ADD Makefile /root/papr/
ADD data /root/papr/data

WORKDIR /root/papr/
RUN ln -s /root/papr/papr/cli.py /usr/bin/papr
ENV PATH=/root/papr:${PATH}
ENV LANG=C.UTF-8

CMD ["/bin/bash"]
