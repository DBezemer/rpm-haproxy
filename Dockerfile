FROM centos:7

RUN yum groupinstall -y 'Development Tools'
RUN mkdir -p /opt && yum install -y wget
WORKDIR /builder

CMD ["make", "build"]
