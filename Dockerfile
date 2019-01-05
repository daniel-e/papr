FROM ubuntu:18.10

RUN apt-get update
RUN apt-get -y install apt-utils aptitude git curl net-tools iputils-ping tcpdump
RUN apt-get -y install python3 python3-pip

RUN pip3 install bs4 termcolor

RUN apt-get -y install jq

RUN echo "alias ..='cd ..'" >> ~/.bashrc
RUN echo "alias l='ls -l'" >> ~/.bashrc

ADD papr /root/papr/papr
ADD scripts /root/papr/scripts
ADD Makefile /root/papr/
 
WORKDIR /root/papr/
RUN ln -s /root/papr/papr/cli.py /usr/bin/papr
ENV PATH=/root/papr:${PATH}

CMD ["/bin/bash"]
