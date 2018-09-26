%define haproxy_user    haproxy
%define haproxy_group   %{haproxy_user}
%define haproxy_home    %{_localstatedir}/lib/haproxy

%if 0%{?rhel} == 7 && 0%{!?amzn2}
    # CentOS 7 forces ".el7.centos", wtf CentOS maintainers...
    %define dist .el7
%endif

%if 0%{?rhel} < 7
    %{!?__global_ldflags: %global __global_ldflags -Wl,-z,relro}
%endif

Summary: HA-Proxy is a TCP/HTTP reverse proxy for high availability environments
Name: haproxy
Version: %{version}
Release: %{release}%{?dist}
License: GPL
Group: System Environment/Daemons
URL: http://www.haproxy.org/
Source0: http://www.haproxy.org/download/1.8/src/%{name}-%{version}.tar.gz
Source1: %{name}.cfg
%{?amzn1:Source2: %{name}.init}
%{?el6:Source2: %{name}.init}
%{?el7:Source2: %{name}.service}
Source3: %{name}.logrotate
Source4: %{name}.syslog%{?dist}
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: pcre-devel make gcc openssl-devel

Requires(pre):      shadow-utils

%if 0%{?el6} || 0%{?amzn1}
Requires(post):     chkconfig, initscripts
Requires(preun):    chkconfig, initscripts
Requires(postun):   initscripts
%endif

%if 0%{?el7} || 0%{?amzn2}
BuildRequires:      systemd-units systemd-devel
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

%if 0%{?el7} || 0%{?amzn2}
systemd_opts="USE_SYSTEMD=1"
pcre_opts="USE_PCRE=1 USE_PCRE_JIT=1"
%else
systemd_opts=
pcre_opts="USE_PCRE=1"
%endif

%{__make} %{?_smp_mflags} CPU="generic" TARGET="linux2628" ${systemd_opts} ${pcre_opts} USE_OPENSSL=1 USE_ZLIB=1 ${regparm_opts} ADDINC="%{optflags}" USE_LINUX_TPROXY=1 ADDLIB="%{__global_ldflags}" DEFINE=-DTCP_USER_TIMEOUT=18

%install
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%{__install} -d %{buildroot}%{_sbindir}
%{__install} -d %{buildroot}%{_sysconfdir}/logrotate.d
%{__install} -d %{buildroot}%{_sysconfdir}/rsyslog.d
%{__install} -d %{buildroot}%{_sysconfdir}/%{name}
%{__install} -d %{buildroot}%{_sysconfdir}/%{name}/errors
%{__install} -d %{buildroot}%{_localstatedir}/log/%{name}
%{__install} -d %{buildroot}%{_mandir}/man1/

%{__install} -s %{name} %{buildroot}%{_sbindir}/
%if 0%{?el6} || 0%{?amzn1}
%{__install} -d %{buildroot}%{_sysconfdir}/rc.d/init.d
%{__install} -c -m 755 %{SOURCE2} %{buildroot}%{_sysconfdir}/rc.d/init.d/%{name}
%endif
%if 0%{?el7} || 0%{?amzn2}
%{__install} -s %{name} %{buildroot}%{_sbindir}/
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
%endif
%{__install} -c -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}/
%{__install} -c -m 755 examples/errorfiles/*.http %{buildroot}%{_sysconfdir}/%{name}/errors/
%{__install} -c -m 755 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -c -m 755 %{SOURCE4} %{buildroot}%{_sysconfdir}/rsyslog.d/49-%{name}.conf
%{__install} -c -m 755 doc/%{name}.1 %{buildroot}%{_mandir}/man1/

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
%if 0%{?el7} || 0%{?amzn2}
%systemd_post %{name}.service
systemctl restart rsyslog.service
%endif

%if 0%{?el6} || 0%{?amzn1}
/sbin/chkconfig --add %{name}
/sbin/service rsyslog restart >/dev/null 2>&1 || :
%endif

%preun
%if 0%{?el7} || 0%{?amzn2}
%systemd_preun %{name}.service
%endif

%if 0%{?el6} || 0%{?amzn1}
if [ $1 = 0 ]; then
  /sbin/service %{name} stop >/dev/null 2>&1 || :
  /sbin/chkconfig --del %{name}
fi
%endif

%postun
%if 0%{?el7} || 0%{?amzn2}
%systemd_postun_with_restart %{name}.service
systemctl restart rsyslog.service
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
%doc %{_mandir}/man1/%{name}.1*
%dir %{_localstatedir}/log/%{name}

%attr(0755,root,root) %{_sbindir}/%{name}
%if 0%{?el6} || 0%{?amzn1}
%attr(0755,root,root) %config %_sysconfdir/rc.d/init.d/%{name}
%endif
%if 0%{?el7} || 0%{?amzn2}
%attr(0755,root,root) %{_sbindir}/%{name}
%attr(-,root,root) %{_unitdir}/%{name}.service
%endif
%dir %{_sysconfdir}/%{name}
%{_sysconfdir}/%{name}/errors
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/%{name}.cfg
%attr(0644,root,root) %config %{_sysconfdir}/logrotate.d/%{name}
%attr(0644,root,root) %config %{_sysconfdir}/rsyslog.d/49-%{name}.conf

%changelog
* Fri Wed Sep 26 2018 J. Casalino <casalino@adobe.com>
- Update to HAproxy 1.8.14

* Fri Jun 29 2018 Topher Cullen <topher@shawlite.com>
- Update to HAproxy 1.8.12
- Add support for Amazon Linux 2

* Thu May 18 2018 David Bezemer <info@davidbezemer.nl>
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
