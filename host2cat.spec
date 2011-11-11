%define webserver_cgibindir	%{_var}/www/cgi-bin/
%define _initdir	/etc/rc.d/init.d
%define _cachedir	/var/cache

Name:		host2cat
Version:	1.02
Release:	1

Summary:	Custom DNS resolver
License:	BSD
Group:		System/Servers
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Url:		www.netpolice.ru

Source0: 	%{name}-%{version}.tar.gz
Source1: 	%{name}.init
Source2: 	%{name}.sysconfig
Source3: 	squid.conf
Source4:	SQLite_migration_1.0.2_to_1.1.sql
Patch:		%{name}-filterdb.patch

# Automatically added by buildreq on Fri Apr 10 2009
BuildRequires:	libadns-devel
BuildRequires:	libmemcache-devel

# for findreq
BuildRequires: 	perl-DBI
BuildRequires:	perl-Net-DNS perl-CGI

# for cgi-bin dir
Requires:	apache-base
Requires:	apache-conf >= 2.0
Requires:	apache-mod_perl
Requires: 	perl-DBD-SQLite
Requires:	memcached
Requires: 	netpolice-filter
Requires: 	squid-conf-%{name}
Requires:	squid >= 3.0

%description
DNS resolver for web content filtering with web interface.

%package -n squid-conf-%{name}
Summary:	adapted squid config
Group:		System/Servers

%description -n squid-conf-%{name}
This package contains squid config adapted for %{name}.

%prep
%setup -q
%patch -p1

%build
aclocal --force
autoconf --force
autoheader --force
automake --add-missing --force-missing --foreign
%configure
%make

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/{%{_cachedir}/%{name},%{webserver_cgibindir},%{_libexecdir}/%{name}}
mkdir -p %{buildroot}/%{_var}/lib/netpolice
mkdir -p %{buildroot}/%{_var}/lib/netpolice/squid

install -m0755 -D %{name} %{buildroot}/%{_sbindir}/%{name}
install -m0755 -D %{SOURCE1} %{buildroot}/%{_initdir}/%{name}
install -m0644 -D %{SOURCE2} %{buildroot}/%{_sysconfdir}/sysconfig/%{name}
install -m0644 -D %{SOURCE3} %{buildroot}/etc/squid/squid.conf.sample
install -m0644 -D %{SOURCE4} %{buildroot}/var/cache/%{name}/SQLite_migration_1.0.2_to_1.1.sql

install -m0755 contrib/get_file.pl %{buildroot}/%{webserver_cgibindir}/get_file.pl
install -m0644 scripts/config.ph %{buildroot}/%{webserver_cgibindir}/config.ph
install -m0755 scripts/*.cgi %{buildroot}/%{webserver_cgibindir}/
install -m0755 scripts/*.pl %{buildroot}/%{_libexecdir}/%{name}/
install -m0644 scripts/*.schema %{buildroot}/%{_libexecdir}/%{name}/
install -m0644 scripts/custom_roles scripts/generic_roles scripts/users %{buildroot}/%{_libexecdir}/%{name}/

touch %{buildroot}%{_cachedir}/%{name}/filter.db

mkdir -p %{buildroot}/%{_sysconfdir}/httpd/conf/{extra-start.d,extra-available,mods-start.d}
cat << EOF > %{buildroot}/%{_sysconfdir}/httpd/conf/extra-start.d/030-host2cat.conf
host2cat=yes
EOF

cat << EOF > %{buildroot}/%{_sysconfdir}/httpd/conf/extra-available/host2cat.conf
<IfModule alias_module>
	ScriptAlias /cgi-bin/ "/var/www/cgi-bin/"
</IfModule>
EOF

cat << EOF > %{buildroot}/%{_sysconfdir}/httpd/conf/mods-start.d/030-host2cat.conf
alias=yes
cgi=yes
EOF

%post
%_post_service %{name}
#/usr/sbin/a2chkconfig &> /dev/null ||:
/sbin/service httpd condreload ||:
INITDB=%{_libexecdir}/%{name}/init_filter_db.pl
[ -x $INITDB ] && $INITDB -d %{_libexecdir}/%{name}/ dbi:SQLite:dbname=%{_cachedir}/%{name}/filter.db ||:
mkdir -p /var/lib/netpolice/squid
touch /var/lib/netpolice/squid/passwd
usr/sbin/htpasswd -b /var/lib/netpolice/squid/passwd netpolice netpolice
%preun
%_preun_service %{name}

%post -n squid-conf-%{name}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_initdir}/%{name}
%{_sysconfdir}/sysconfig/%{name}
%{_sysconfdir}/httpd/conf/extra-start.d/030-host2cat.conf
%{_sysconfdir}/httpd/conf/extra-available/host2cat.conf
%{_sysconfdir}/httpd/conf/mods-start.d/030-host2cat.conf
%{_sbindir}/%{name}
%{webserver_cgibindir}/get_file.pl
%{_libexecdir}/%{name}
%config(noreplace) %{webserver_cgibindir}/config.ph
%{webserver_cgibindir}/*.cgi
%dir %attr(711,apache,root) %{_cachedir}/%{name}
%config(noreplace )%attr(644,apache,root) %{_cachedir}/%{name}/filter.db
/var/cache/%{name}/SQLite_migration_1.0.2_to_1.1.sql

%files -n squid-conf-%{name}
%defattr(-,root,root)
%config(noreplace) /etc/squid/squid.conf.sample

%changelog
* Fri Aug 5 2011 L.Butorina <l.butorina@cair.ru> 1
- New test version host2cat 1.02 for Mandriva.


