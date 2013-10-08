#
# Conditional build
%bcond_without	tests		# make check
%bcond_without	java		# build java subpackage

%if "%{pld_release}" == "ac"
%ifnarch i586 i686 pentium3 pentium4 athlon %{x8664}
%undefine	with_java
%endif
%endif

%define		tzcode_ver	2013g
%define		tzdata_ver	2013g
Summary:	Timezone data
Summary(pl.UTF-8):	Dane o strefach czasowych
Name:		tzdata
Version:	%{tzdata_ver}
Release:	1
License:	Public Domain (database), BSD/LGPL v2.1+ (code/test suite)
Group:		Base
# The tzdata-base-0.tar.bz2 is a simple building infrastructure and
# a test suite. It is occasionally updated from glibc sources, and as
# such is under LGPL v2+, but none of this ever gets to be part of
# final zoneinfo files.
Source0:	%{name}-base-0.tar.bz2
# Source0-md5:	e36d2f742c22f8c8dbf0686ac9769b55
# ftp://elsie.nci.nih.gov/pub/ has been shut down because of lawsuit
#Source1Download: http://www.iana.org/time-zones/
Source1:	ftp://ftp.iana.org/tz/releases/%{name}%{tzdata_ver}.tar.gz
# Source1-md5:	76dbc3b5a81913fc0d824376c44a5d15
#Source2Download: http://www.iana.org/time-zones/
Source2:	ftp://ftp.iana.org/tz/releases/tzcode%{tzcode_ver}.tar.gz
# Source2-md5:	cc2a52297310ba1a673dc60973ea3ad8
Source3:	timezone.init
Source4:	timezone.sysconfig
Source5:	javazic.tar.gz
# Source5-md5:	6a3392cd5f1594d13c12c1a836ac8d91
Source6:	timezone.upstart
Source7:	timezone.service
Source8:	timezone.sh
Patch1:		javazic-fixup.patch
Patch2:		install.patch
URL:		http://www.twinsun.com/tz/tz-link.htm
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpmbuild(macros) >= 1.623
%if %{with java}
BuildRequires:	jdk
BuildRequires:	jpackage-utils
BuildRequires:	rpm-javaprov
%endif
Requires(post,preun,postun):	systemd-units >= 38
Requires:	/sbin/chkconfig
Requires:	rc-scripts >= 0.4.3.0
Requires:	systemd-units >= 38
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This package contains data files with rules for various timezones
around the world.

%description -l pl.UTF-8
Ten pakiet zawiera pliki z danymi na temat reguł stref czasowych na
całym świecie.

%package -n java-tzdata
Summary:	Timezone data for Java
Summary(pl.UTF-8):	Dane stref czasowych dla Javy
Group:		Base

%description -n java-tzdata
This package contains timezone information for use by Java runtimes.

%description -n java-tzdata -l pl.UTF-8
Ten pakiet zawiera informacje o strefach czasowych przeznaczone dla
programów w Javie.

%package zoneinfo_right
Summary:	Non-POSIX (real) time zones
Summary(es.UTF-8):	Zonas de tiempo reales (no de POSIX)
Summary(pl.UTF-8):	Nie-POSIX-owe (prawdziwe) strefy czasowe
Group:		Libraries
Obsoletes:	glibc-zoneinfo_right

%description zoneinfo_right
You don't want this. Details at:
<http://sources.redhat.com/ml/libc-alpha/2000-12/msg00068.html>.

%description zoneinfo_right -l es.UTF-8
No lo necesita. Encontrará los detalles en:
<http://sources.redhat.com/ml/libc-alpha/2000-12/msg00068.html>.

%description zoneinfo_right -l pl.UTF-8
Nie potrzebujesz tego. Szczegóły pod:
<http://sources.redhat.com/ml/libc-alpha/2000-12/msg00068.html>.

%package devel
Summary:	tzfile header file
Summary(pl.UTF-8):	Plik nagłówkowy tzfile
Group:		Development/Libraries

%description devel
Header file for timezone database.

%description devel -l pl.UTF-8
Plik nagłówkowy bazy danych stref czasowych.

%prep
%setup -qc
mv tzdata/* .
%{__tar} xzf %{SOURCE1} -C tzdata
# don't override Makefile from base tar
mv tzdata/Makefile{,.tzdata}
install -d tzcode
%{__tar} xzf %{SOURCE2} -C tzcode
%patch2 -p1

%{__sed} -e "
s|@objpfx@|`pwd`/obj/|
s|@datadir@|%{_datadir}|
s|@install_root@|$RPM_BUILD_ROOT|
" 'Makeconfig.in' > Makeconfig

grep -v tz-art.htm tzcode/tz-link.htm > tzcode/tz-link.html

%if %{with java}
install -d javazic
tar zxf %{SOURCE5} -C javazic
cd javazic
%patch1

# Hack alert! sun.tools may be defined and installed in the
# VM. In order to guarantee that we are using IcedTea/OpenJDK
# for creating the zoneinfo files, rebase all the packages
# from "sun." to "rht.". Unfortunately, gcj does not support
# any of the -Xclasspath options, so we must go this route
# to ensure the greatest compatibility.
# XXX: do we want 'pld' instead of 'rht'?
mv sun rht
find . -type f -name '*.java' -print0 \
	| xargs -0 -- sed -i -e 's:sun\.tools\.:rht.tools.:g' \
						 -e 's:sun\.util\.:rht.util.:g'
cd -
%endif

%build
%{__make}

%if %{with java}
cd javazic
%javac -source 1.5 -target 1.5 -classpath . $(find -name '*.java')
cd ../tzdata
%java -classpath ../javazic/ rht.tools.javazic.Main -V %{version} \
	-d ../zoneinfo/java \
	africa antarctica asia australasia europe northamerica pacificnew \
	southamerica backward etcetera solar87 solar88 solar89 systemv \
	../javazic/tzdata_jdk/gmt ../javazic/tzdata_jdk/jdk11_backward
cd ..
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{sysconfig,rc.d/init.d},%{_mandir}/man5,%{_includedir},%{systemdunitdir}}
%{__make} install

%if %{with tests}
# test needs to be ran after "make install", as it uses installed files
: ====================TESTING=========================
%{__make} check \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} %{rpmldflags}"
: ====================TESTING END=====================
%endif

# glibc.spec didn't keep it. so won't here either.
%{__rm} -r $RPM_BUILD_ROOT%{_datadir}/zoneinfo/posix
# behave more like glibc.spec
ln -sf %{_sysconfdir}/localtime	$RPM_BUILD_ROOT%{_datadir}/zoneinfo/localtime
ln -sf localtime $RPM_BUILD_ROOT%{_datadir}/zoneinfo/posixtime
ln -sf localtime $RPM_BUILD_ROOT%{_datadir}/zoneinfo/posixrules

> $RPM_BUILD_ROOT/etc/localtime

# header file
cp -p tzcode/tzfile.h $RPM_BUILD_ROOT%{_includedir}/tzfile.h
cp -p tzcode/tzfile.5 $RPM_BUILD_ROOT%{_mandir}/man5

install -p %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/timezone
cp -p %{SOURCE4} $RPM_BUILD_ROOT/etc/sysconfig/timezone

install -d $RPM_BUILD_ROOT/etc/init
cp -p %{SOURCE6} $RPM_BUILD_ROOT/etc/init/timezone.conf

install -p %{SOURCE7} $RPM_BUILD_ROOT%{systemdunitdir}/timezone.service
install -p %{SOURCE8} $RPM_BUILD_ROOT/lib/systemd/pld-timezone

%if %{with java}
cp -a zoneinfo/java $RPM_BUILD_ROOT%{_datadir}/javazi
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add timezone
%service timezone restart
%systemd_post timezone.service

%preun
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del timezone

	# save for postun
	cp -af /etc/localtime /etc/localtime.rpmsave
fi
%systemd_preun timezone.service

%postun
if [ "$1" = "0" ]; then
	if [ ! -f /etc/localtime -a -f /etc/localtime.rpmsave ]; then
		echo >&2 "Preserving /etc/localtime"
		mv -f /etc/localtime{.rpmsave,}
	fi
fi
%systemd_reload

%triggerpostun -- rc-scripts < 0.4.1.4
/sbin/chkconfig --add timezone

%triggerpostun -- tzdata < 2008b-4
if ! grep -q '^TIMEZONE=' /etc/sysconfig/timezone; then
	. /etc/sysconfig/timezone

	if [ -z $ZONE_INFO_AREA ]; then
		TIMEZONE=$TIME_ZONE
	else
		TIMEZONE=$ZONE_INFO_AREA/$TIME_ZONE
	fi

	echo "TIMEZONE=\"$TIMEZONE\"" >> /etc/sysconfig/timezone

	%service timezone restart
fi

%triggerpostun -- tzdata < 2012a-2
%systemd_trigger timezone.service

%files
%defattr(644,root,root,755)
%doc tzcode/README tzcode/Theory tzcode/tz-link.html
%ghost /etc/localtime
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/timezone
%attr(754,root,root) /etc/rc.d/init.d/timezone
%config(noreplace) %verify(not md5 mtime size) /etc/init/timezone.conf
%{systemdunitdir}/timezone.service
%attr(755,root,root) /lib/systemd/pld-timezone

%{_datadir}/zoneinfo
%exclude %{_datadir}/zoneinfo/right

%if %{with java}
%files -n java-tzdata
%defattr(644,root,root,755)
%{_datadir}/javazi
%endif

%files zoneinfo_right
%defattr(644,root,root,755)
%{_datadir}/zoneinfo/right

%files devel
%defattr(644,root,root,755)
%doc tzcode/tzfile.5.txt
%{_includedir}/tzfile.h
%{_mandir}/man5/tzfile.5*
