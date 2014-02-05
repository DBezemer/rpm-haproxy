# A Recipe for a haproxy 1.5 development version (v22) RPM on CentOS

Perform the following on a build box as a regular user.

## Create an RPM Build Environment

Install rpmdevtools from the [EPEL][epel] repository:

    sudo yum install rpmdevtools pcre-devel
    rpmdev-setuptree

## Install Prerequisites for RPM Creation

    sudo yum groupinstall 'Development Tools'
    sudo yum install openssl-devel

## Download haproxy

    wget http://haproxy.1wt.eu/download/1.5/src/devel/haproxy-1.5-dev22.tar.gz
    mv http://haproxy.1wt.eu/download/1.5/src/devel/haproxy-1.5-dev22.tar.gz ~/rpmbuild/SOURCES/

## Get Necessary System-specific Configs

    git clone git://github.com/bluerail/haproxy-centos.git
    cp haproxy-centos/conf/* ~/rpmbuild/SOURCES/
    cp haproxy-centos/spec/* ~/rpmbuild/SPECS/

## Build the RPM

    cd ~/rpmbuild/
    rpmbuild -ba SPECS/haproxy.spec

The resulting RPM will be in ~/rpmbuild/RPMS/x86_64

## Credits

Based on the Red Hat 6.4 RPM spec for haproxy 1.4.

Maintained by [Martijn Storck](martijn@bluerail.nl)

[EPEL]: http://fedoraproject.org/wiki/EPEL#How_can_I_use_these_extra_packages.3F
