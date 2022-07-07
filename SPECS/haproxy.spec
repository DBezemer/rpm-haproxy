%define haproxy_user    haproxy
%define haproxy_group   %{haproxy_user}
%define haproxy_home    %{_localstatedir}/lib/haproxy

%if 0%{?rhel} > 6 && 0%{!?amzn2}
    %define dist %{expand:%%(/usr/lib/rpm/redhat/dist.sh --dist)}
%endif

%if 0%{?rhel} < 7
    %{!?__global_ldflags: %global __global_ldflags -Wl,-z,relro}
%endif

%global _hardened_build 1

Summary: HA-Proxy reverse proxy for high availability environments
Name: haproxy
Version: %{version}
Release: %{release}%{?dist}
License: GPLv2+
Group: System Environment/Daemons
URL: http://www.haproxy.org/
Source0: http://www.haproxy.org/download/%{mainversion}/src/%{name}-%{version}.tar.gz
Source1: %{name}.cfg
%if 0%{?el6} || 0%{?amzn1}
Source2: %{name}.init
%else
Source2: %{name}.service
%endif
Source3: %{name}.logrotate
Source4: %{name}.syslog%{?dist}
Source5: halog.1
BuildRoot: %{_tmppath}/%{name}-%{version}-root

BuildRequires: pcre-devel
BuildRequires: zlib-devel
BuildRequires: make
BuildRequires: gcc openssl-devel
BuildRequires: openssl-devel

Requires(pre):      shadow-utils
Requires:           rsyslog

%if 0%{?el6} || 0%{?amzn1}
Requires(post):     chkconfig, initscripts
Requires(preun):    chkconfig, initscripts
Requires(postun):   initscripts
%endif

%if 0%{?el7} || 0%{?amzn2} || 0%{?el8} || 0%{?el9}
BuildRequires:      systemd-units
BuildRequires:      systemd-devel
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd
%endif

%description
HA-Proxy is a TCP/HTTP reverse proxy which is particularly suited for high
availability environments. Indeed, it can:
- route HTTP requests depending on statically assigned cookies
- spread the load among several servers while assuring server persistence
  through the use of HTTP cookies
- switch to backup servers in the event a main one fails
- accept connections to special ports dedicated to service monitoring
- stop accepting connections without breaking existing ones
- add/modify/delete HTTP headers both ways
- block requests matching a particular pattern

It needs very little resource. Its event-driven architecture allows it to easily
handle thousands of simultaneous connections on hundreds of instances without
risking the system's stability.

%prep
%setup -q

# We don't want any perl dependecies in this RPM:
%define __perl_requires /bin/true

%build
regparm_opts=
%ifarch %ix86 x86_64
regparm_opts="USE_REGPARM=1"
%endif

RPM_BUILD_NCPUS="`/usr/bin/nproc 2>/dev/null || /usr/bin/getconf _NPROCESSORS_ONLN`";

# Default opts
systemd_opts=
pcre_opts="USE_PCRE=1"
CFLAGS="%{optflags}"
USE_TFO=
USE_NS=

%if 0%{?el7} || 0%{?amzn2} || 0%{?el8} || 0%{?el9}
systemd_opts="USE_SYSTEMD=1"
pcre_opts="USE_PCRE=1 USE_PCRE_JIT=1"
%endif

%if 0%{?el7} || 0%{?amzn2} || 0%{?amzn1} || 0%{?el8} || 0%{?el9}
USE_TFO=1
USE_NS=1
%endif

%if 0%{_use_lua}
USE_LUA="USE_LUA=1"
%endif

%if 0%{_use_prometheus}
USE_PROMETHEUS="USE_PROMEX=1"
%endif

%if "%{_extra_cflags}" != "0"
  CFLAGS="$CFLAGS %{_extra_cflags}"
%endif

%{__make} -j$RPM_BUILD_NCPUS %{?_smp_mflags} ${USE_LUA} CPU="generic" TARGET="linux-glibc" ${systemd_opts} ${pcre_opts} USE_OPENSSL=1 USE_ZLIB=1 ${regparm_opts} ADDINC="$CFLAGS" USE_LINUX_TPROXY=1 USE_THREAD=1 USE_TFO=${USE_TFO} USE_NS=${USE_NS} ${USE_PROMETHEUS} ADDLIB="%{__global_ldflags}"

%{__make} admin/halog/halog OPTIMIZE="%{optflags} %{__global_ldflags}"

%{__make} admin/iprange/iprange OPTIMIZE="%{optflags} %{__global_ldflags}"

%{__make} admin/iprange/ip6range OPTIMIZE="%{optflags} %{__global_ldflags}"

%install
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%{__install} -d %{buildroot}%{_sbindir}
%{__install} -d %{buildroot}%{_bindir}
%{__install} -d %{buildroot}%{_sysconfdir}/%{name}
%{__install} -d %{buildroot}%{_sysconfdir}/%{name}/errors
%{__install} -d %{buildroot}%{_mandir}/man1/
%{__install} -d %{buildroot}%{_sysconfdir}/logrotate.d
%{__install} -d %{buildroot}%{_sysconfdir}/rsyslog.d
%{__install} -d %{buildroot}%{_localstatedir}/log/%{name}

%{__install} -p %{name} %{buildroot}%{_sbindir}/


%{__install} -c -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}/haproxy.cfg
%{__install} -c -m 644 examples/errorfiles/*.http %{buildroot}%{_sysconfdir}/%{name}/errors/
%{__install} -c -m 644 doc/%{name}.1 %{buildroot}%{_mandir}/man1/
%{__install} -c -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/rsyslog.d/49-%{name}.conf
%{__install} -c -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%{__install} -p -m 0755 ./admin/halog/halog %{buildroot}%{_bindir}/halog
%{__install} -p -m 0755 ./admin/iprange/iprange %{buildroot}%{_bindir}/iprange
%{__install} -p -m 0755 ./admin/iprange/ip6range %{buildroot}%{_bindir}/ip6range
%{__install} -p -D -m 0644 %{SOURCE5} %{buildroot}%{_mandir}/man1/halog.1

%if 0%{?el6} || 0%{?amzn1}
%{__install} -d %{buildroot}%{_sysconfdir}/rc.d/init.d
%{__install} -c -m 755 %{SOURCE2} %{buildroot}%{_sysconfdir}/rc.d/init.d/%{name}
%endif

%if 0%{?el7} || 0%{?amzn2} || 0%{?el8} || 0%{?el9}
%{__install} -s %{name} %{buildroot}%{_sbindir}/
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
%endif

%clean
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%pre
getent group %{haproxy_group} >/dev/null || \
       groupadd -g 188 -r %{haproxy_group}
getent passwd %{haproxy_user} >/dev/null || \
       useradd -u 188 -r -g %{haproxy_group} -d %{haproxy_home} \
       -s /sbin/nologin -c "%{name}" %{haproxy_user}
exit 0

%post
%if 0%{?el7} || 0%{?amzn2} || 0%{?el8} || 0%{?el9}
%systemd_post %{name}.service
systemctl reload-or-try-restart rsyslog.service
%endif

%if 0%{?el6} || 0%{?amzn1}
/sbin/chkconfig --add %{name}
/sbin/service rsyslog restart >/dev/null 2>&1 || :
%endif

%preun
%if 0%{?el7} || 0%{?amzn2} || 0%{?el8} || 0%{?el9}
%systemd_preun %{name}.service
%endif

%if 0%{?el6} || 0%{?amzn1}
if [ $1 = 0 ]; then
  /sbin/service %{name} stop >/dev/null 2>&1 || :
  /sbin/chkconfig --del %{name}
fi
%endif

%postun
%if 0%{?el7} || 0%{?amzn2} || 0%{?el8} || 0%{?el9}
%systemd_postun_with_restart %{name}.service
systemctl reload-or-try-restart rsyslog.service
%endif

%if 0%{?el6} || 0%{?amzn1}
if [ "$1" -ge "1" ]; then
  /sbin/service %{name} condrestart >/dev/null 2>&1 || :
  /sbin/service rsyslog restart >/dev/null 2>&1 || :
fi
%endif

%files
%defattr(-,root,root)
%doc CHANGELOG README examples/*.cfg doc/architecture.txt doc/configuration.txt doc/intro.txt doc/management.txt doc/proxy-protocol.txt
%if 0%{?el7} || 0%{?amzn2} || 0%{?el8} || 0%{?el9}
    %license LICENSE
%endif
%doc %{_mandir}/man1/*
%dir %{_sysconfdir}/%{name}
%{_sysconfdir}/%{name}/errors
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/%{name}.cfg
%attr(0755,root,root) %{_sbindir}/%{name}
%dir %{_localstatedir}/log/%{name}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/rsyslog.d/49-%{name}.conf
%{_bindir}/halog
%{_bindir}/iprange
%{_bindir}/ip6range

%if 0%{?el6} || 0%{?amzn1}
%attr(0755,root,root) %config %_sysconfdir/rc.d/init.d/%{name}
%endif

%if 0%{?el7} || 0%{?amzn2} || 0%{?el8} || 0%{?el9}
%attr(-,root,root) %{_unitdir}/%{name}.service
%endif

%changelog
* Thu Feb 10 2022 Karsten Horsmann <khorsmann@gmail.com>
- Add Docker support for RHEL 9.0 / Almalinux 9.0

* Thu Feb 10 2022 Kai Parry <tp@threadproc.io>
- Add Docker support for Amazon Linux 2

* Sat May 30 2021 David Bezemer <info@davidbezemer.nl>
- Add support for HAProxy 2.4.x

* Sun Apr 11 2021 David Bezemer <info@davidbezemer.nl>
- Add support for HAProxy 2.3.x

* Sun Jul 12 2020 David Bezemer <info@davidbezemer.nl>
- Backwards compatible conditional restart using reload-or-try-restart

* Sun Jul 12 2020 David Bezemer <info@davidbezemer.nl>
- Add support for HAProxy 2.1.x

* Sat Jun 13 2020 David Bezemer <info@davidbezemer.nl>
- Add conditional prometheus module support by mfilz

* Tue Feb 25 2020 David Bezemer <info@davidbezemer.nl>
- Fix conditional LUA building
- Add readline-devel as dependency for lua building

* Tue Feb 25 2020 J. Casalino <casalino@adobe.com>
- Add support for HAProxy 2.1.x

* Tue Feb 25 2020 Davasny <davasny@gmail.com>
- Add conditional LUA building

* Tue Nov 19 2019 J. Casalino <casalino@adobe.com>
- Only reset dist variable with dist.sh script if dist is CentOS/RHEL>6 and not Amazon Linux 2

* Sun Oct 20 2019 David Bezemer <info@davidbezemer.nl>
- Add compatiblity with CentOS/RHEL 8

* Tue Jun 18 2019 David Bezemer <info@davidbezemer.nl>
- First build of HAproxy 2.0.0

* Tue Jun 18 2019 David Bezemer <info@davidbezemer.nl>
- Update to HAproxy 1.9.8

* Wed Sep 26 2018 J. Casalino <casalino@adobe.com>
- Update to HAproxy 1.8.14

* Fri Jun 29 2018 Topher Cullen <topher@shawlite.com>
- Update to HAproxy 1.8.12
- Add support for Amazon Linux 2

* Fri May 18 2018 David Bezemer <info@davidbezemer.nl>
- Update to HAproxy 1.8.8

* Fri Feb 23 2018 J. Casalino <casalino@adobe.com>
- Add support for Amazon Linux (Fedora-based)

* Mon Feb 12 2018 David Bezemer <info@davidbezemer.nl>
- Update to HAproxy 1.8.4

* Fri Jan 26 2018 Kamil Herbik <kamil.herbik@rst.com.pl>
- Update for HAproxy 1.8

* Mon Jul 31 2017 David Bezemer <info@davidbezemer.nl>
- Update for HAproxy 1.7.8

* Thu Jun 08 2017 David Bezemer <info@davidbezemer.nl>
- Update for HAproxy 1.7.5
- Remove duplicate pcre-devel requirement

* Sun Jan 15 2017 David Bezemer <info@davidbezemer.nl>
- Update for HAproxy 1.7.2

* Sun Oct 23 2016 David Bezemer <info@davidbezemer.nl>
- Add systemd compatibility

* Sat Oct 22 2016 David Bezemer <info@davidbezemer.nl>
- reworked installation structure
- included rsylog config for logging
- copy default error files
- updated to 1.6.9
