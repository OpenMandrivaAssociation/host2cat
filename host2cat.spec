%define webserver_cgibindir %_var/www/cgi-bin/

Name: host2cat
Version: 1.01
Release: 2%{?dist}
Packager: CAIR <support@cair.ru>

Summary: Custom DNS resolver
License: BSD
Group: System/Servers
Url: www.netpolice.ru

Source0: %name-%version.tar.gz
Source1: %name.init
Source2: %name.sysconfig
Source3: squid.conf

# Automatically added by buildreq on Fri Apr 10 2009
BuildRequires: adns-devel libmemcache-devel

# for findreq 
BuildRequires: perl-DBI perl-Net-DNS

# for cgi-bin dir
Requires: apache-conf >= 2.0 apache-mod_perl
Requires: perl-DBD-SQLite memcached

Requires: netpolice-filter squid-conf-%name squid >= 3.0

%description
DNS resolver for web content filtering with web interface

%package -n squid-conf-%name
Summary: adapted squid config
Group: System/Servers
Provides: squid-conf = %version-%release, %_sysconfdir/squid/squid.conf.sample
%{expand:%%global o_list %(for n in default; do echo -n "squid-conf-$n "; done)}
%{?o_list:Conflicts: %o_list}

%description -n squid-conf-%name
This package contains squid config adapted for %name

%prep
%setup -q

%build
aclocal --force 
autoconf --force
autoheader --force
automake --add-missing --force-missing --foreign
%configure
make

%install
mkdir -p $RPM_BUILD_ROOT{/var/cache/%name,%webserver_cgibindir,%_libexecdir/%name}

install -m0755 -D %name $RPM_BUILD_ROOT%_sbindir/%name
install -m0755 -D %SOURCE1 $RPM_BUILD_ROOT/etc/rc.d/init.d/%name
install -m0644 -D %SOURCE2 $RPM_BUILD_ROOT%_sysconfdir/sysconfig/%name.default
install -m0644 -D %SOURCE3 $RPM_BUILD_ROOT%_sysconfdir/squid/squid.conf.sample

install -m0755 contrib/get_file.pl $RPM_BUILD_ROOT%webserver_cgibindir/get_file_host.pl
install -m0644 scripts/config.ph $RPM_BUILD_ROOT%webserver_cgibindir/config.ph
install -m0755 scripts/*.cgi $RPM_BUILD_ROOT%webserver_cgibindir/
install -m0755 scripts/*.pl $RPM_BUILD_ROOT%_libexecdir/%name/
install -m0644 scripts/*.schema $RPM_BUILD_ROOT%_libexecdir/%name/
install -m0644 scripts/custom_roles scripts/generic_roles scripts/users $RPM_BUILD_ROOT%_libexecdir/%name/

touch $RPM_BUILD_ROOT/var/cache/%name/filter.db.default

mkdir -p $RPM_BUILD_ROOT%_sysconfdir/httpd/conf/{extra-start.d,extra-available,mods-start.d}
cat << EOF > $RPM_BUILD_ROOT%_sysconfdir/httpd/conf/extra-start.d/030-host2cat.conf
host2cat=yes
EOF

cat << EOF > $RPM_BUILD_ROOT%_sysconfdir/httpd/conf/extra-available/host2cat.conf
<IfModule alias_module>
	ScriptAlias /cgi-bin/ "/var/www/cgi-bin/"
</IfModule>
EOF

cat << EOF > $RPM_BUILD_ROOT%_sysconfdir/httpd/conf/mods-start.d/030-host2cat.conf
alias=yes
cgi=yes
EOF

%post
/usr/sbin/a2chkconfig &> /dev/null ||:
/sbin/service httpd condrestart ||:
INITDB=%_libexecdir/%name/init_filter_db.pl
[ -x $INITDB ] && $INITDB -d %_libexecdir/%name/ dbi:SQLite:dbname=/var/cache/%name/filter.db.default ||:

%post -n squid-conf-%name
touch %_sysconfdir/squid/passwd
htpasswd -b %_sysconfdir/squid/passwd netpolice netpolice

%files
/etc/rc.d/init.d/%name
%config(noreplace) %_sysconfdir/sysconfig/%name.default
%_sysconfdir/httpd/conf/extra-start.d/030-host2cat.conf
%_sysconfdir/httpd/conf/extra-available/host2cat.conf
%_sysconfdir/httpd/conf/mods-start.d/030-host2cat.conf
%_sbindir/%name
%webserver_cgibindir/get_file_host.pl
%_libexecdir/%name
%config(noreplace) %webserver_cgibindir/config.ph
%webserver_cgibindir/*.cgi
%dir %attr(711,apache,root) /var/cache/%name
%attr(644,apache,root) /var/cache/%name/filter.db.default
%config(noreplace) /var/cache/%name/filter.db.default

%files -n squid-conf-%name
%config(noreplace) %_sysconfdir/squid/squid.conf.sample

%clean
make clean
rm -rf $RPM_BUILD_ROOT

