FROM centos:7

ARG USE_LUA
RUN yum install -y wget pcre-devel make gcc openssl-devel rpm-build systemd-devel wget sed zlib-devel
RUN mkdir RPMS
RUN chmod -R 777 RPMS
RUN mkdir SPECS
RUN mkdir SOURCES
COPY Makefile Makefile
COPY SPECS/haproxy.spec SPECS/haproxy.spec
COPY SOURCES/* SOURCES/

CMD make NO_SUDO=1 USE_LUA=${USE_LUA} && cp /rpmbuild/RPMS/x86_64/* /RPMS && cp /rpmbuild/SRPMS/* /RPMS