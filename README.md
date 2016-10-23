# A Recipe for a haproxy 1.5 stable version RPM on CentOS

Perform the following on a build box as a regular user.

## Create an RPM Build Environment

Install rpmdevtools from the [EPEL][epel] repository:

    sudo yum install rpmdevtools pcre-devel
    rpmdev-setuptree

## Install Prerequisites for RPM Creation

    sudo yum groupinstall 'Development Tools'

## Checkout this repository

    cd /opt
    git clone https://github.com/DBezemer/rpm-haproxy.git 
    cd ./rpm-haproxy

## Build using makefile
    make
    
Resulting RPM will be in /opt/rpm-haproxy/rpmbuild/RPMS/

## Credits

Based on the Red Hat 6.4 RPM spec for haproxy 1.4 combined with work done by @nmilford @resmo and @kevholmes

