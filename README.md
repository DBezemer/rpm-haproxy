[![Github All Releases](https://img.shields.io/github/downloads/DBezemer/rpm-haproxy/total.svg)](https://github.com/DBezemer/rpm-haproxy/releases) [![Build RPMs](https://github.com/DBezemer/rpm-haproxy/actions/workflows/main.yml/badge.svg)](https://github.com/DBezemer/rpm-haproxy/actions/workflows/main.yml)

This repository contains build artifacts of HAproxy that are provided with no support and no expectation of stability.
The recommended way of using the repository is to build and test your own packages. Latest Work-in-Progress builds can be found under release label "WiP RPM Build".

# RPM Specs for HAproxy on CentOS / RHEL / Amazon Linux with syslog logging to separate output files

## Contributing
When you like to see a specific feature added RPM build process, or support other RPM based Operating Systems please create a Pull Request if you have the knowledge to develop this yourself, I will verify the build process with these changes and merge in upstream when finished. If you don't have the knowledge feel free to create an Issue with the "enhancement" label added. There should be no expectation of when/if this will be added but will allow for tracking what features are of public interest.

Perform the following steps on a build box as a regular user.

## Install Prerequisites for RPM Creation

    sudo yum groupinstall 'Development Tools'

## Checkout this repository

    cd /opt
    git clone https://github.com/DBezemer/rpm-haproxy.git
    cd ./rpm-haproxy
    git checkout dev

## Build using makefile and latest point release of haproxy
### Basic building, no additional components
    make

### Build forcing minor version 2.6 of haproxy, no additional components. Any valid release version can be specified.
    make MAINVERSION=2.6

### With Lua support
    make USE_LUA=1

### With Prometheus Module support
    make USE_PROMETHEUS=1

### Without sudo for yum (for building in Docker)
    make NO_SUDO=1

### With a custom release iteration, e.g. '2' (default '1'):
    make RELEASE=2

### Custom CFLAGS, e.g. '-O0' to disable optimization for debug:
    make EXTRA_CFLAGS=-O0

Resulting RPMs will be in `/opt/rpm-haproxy/rpmbuild/RPMS/x86_64/`

## Build using Docker
    make run-docker

Resulting RPMs will be in `./RPMS/`
When updating any of the files that are included in the build phase, ensure that you also bump the release number, like so:
    make USE_PROMETHEUS=1 RELEASE=3 run-docker

## Credits

Based on the Red Hat 6.4 RPM spec for haproxy 1.4 combined with work done by
- [@nmilford](https://www.github.com/nmilford)
- [@resmo](https://www.github.com/resmo)
- [@kevholmes](https://www.github.com/kevholmes)
- Update to 1.8 contributed by [@khdevel](https://github.com/khdevel)
- Amazon Linux support contributed by [@thedoc31](https://github.com/thedoc31) and [@jazzl0ver](https://github.com/jazzl0ver)
- Version detect snippet by [@hiddenstream](https://github.com/hiddenstream)
- Conditional Lua build support by [@Davasny](https://github.com/Davasny)
- Conditional Prometheus support by [@mfilz](https://github.com/mfilz)
- Debug Building and Dynamic Release version support by [@bugfood](https://github.com/bugfood)
- Macrofication of SUDO option by [@kenstir](https://github.com/kenstir)
- Amazon Linux 2023 support by [@izzyleung](https://github.com/izzyleung)

Additional logging inspired by https://www.percona.com/blog/2014/10/03/haproxy-give-me-some-logs-on-centos-6-5/
