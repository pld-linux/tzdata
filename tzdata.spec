#
# Conditional build
%bcond_without	tests		# make check
%bcond_without	java		# build java subpackage

%ifnarch %{x8664}
# TODO: add more archs which pass tests
# tests fail with 32-bit time_t; reenable after transition to 64-bit everywhere
%undefine	with_tests
%endif

%if "%{pld_release}" == "ac"
%ifnarch i586 i686 pentium3 pentium4 athlon %{x8664}
%undefine	with_java
%endif
%endif

%if %{with java}
%{?use_default_jdk}
%endif

Summary:	Timezone data
Summary(pl.UTF-8):	Dane o strefach czasowych
Name:		tzdata
Version:	2024a
Release:	1
License:	Public Domain (database), BSD/LGPL v2.1+ (code/test suite)
Group:		Base
#Source0Download: https://www.iana.org/time-zones
Source0:	https://www.iana.org/time-zones/repository/releases/tzdb-%{version}.tar.lz
# Source0-md5:	8e21c859fffa2839f5f8cdec3000b64e
Source3:	timezone.init
Source4:	timezone.sysconfig
Source5:	javazic.tar.gz
# Source5-md5:	6a3392cd5f1594d13c12c1a836ac8d91
Patch0:		disable-network-tests.patch
Patch1:		javazic-fixup.patch
Patch2:		install.patch
URL:		http://www.twinsun.com/tz/tz-link.htm
BuildRequires:	lzip
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpmbuild(macros) >= 2.021
%if %{with java}
%buildrequires_jdk
BuildRequires:	jpackage-utils
BuildRequires:	rpm-javaprov
%endif
Requires(post,preun,postun):	systemd-units >= 38
Requires:	%{name}-zoneinfo = %{version}-%{release}
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

%package zoneinfo
Summary:	Timezone data
Summary(pl.UTF-8):	Dane stref czasowych
Group:		Base

%description zoneinfo
Timezone data.

%description zoneinfo -l pl.UTF-8
Dane stref czasowych.

%package zoneinfo_right
Summary:	Non-POSIX (real) time zones
Summary(es.UTF-8):	Zonas de tiempo reales (no de POSIX)
Summary(pl.UTF-8):	Nie-POSIX-owe (prawdziwe) strefy czasowe
Group:		Base
Obsoletes:	glibc-zoneinfo_right < 6:2.3.6-6

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
%setup -qn tzdb-%{version}
%patch -P0 -p1

sed -i -e '/tz-art.html/d' tz-link.html

%if %{with java}
install -d javazic
tar zxf %{SOURCE5} -C javazic --no-same-owner
cd javazic
%patch -P1

# Hack alert! sun.tools may be defined and installed in the
# VM. In order to guarantee that we are using IcedTea/OpenJDK
# for creating the zoneinfo files, rebase all the packages
# from "sun." to "rht.". Unfortunately, gcj does not support
# any of the -Xclasspath options, so we must go this route
# to ensure the greatest compatibility.
# XXX: do we want 'pld' instead of 'rht'?
%{__mv} sun rht
find . -type f -name '*.java' -print0 \
	| xargs -0 -- sed -i -e 's:sun\.tools\.:rht.tools.:g' \
						 -e 's:sun\.util\.:rht.util.:g'
cd -
%endif

%build
# build "fat" zoneinfo files for older parsers (like pytz)
# which can't parse "slim" 64-bit files
%{__make} \
	CFLAGS="%{rpmcflags}" \
	LDFLAGS="%{rpmldflags}" \
	ZFLAGS="-b fat" \
	CC="%{__cc}"

%if %{with java}
cd javazic
%javac -source 1.7 -target 1.7 -classpath . $(find -name '*.java')
cd ..

%java -classpath javazic/ rht.tools.javazic.Main -V %{version} \
	-d zoneinfo/java \
	africa antarctica asia australasia europe northamerica \
	southamerica backward etcetera factory \
	javazic/tzdata_jdk/gmt javazic/tzdata_jdk/jdk11_backward
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{sysconfig,rc.d/init.d},%{_mandir}/man5,%{_includedir},%{systemdunitdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	ZFLAGS="-b fat"

%{__rm} $RPM_BUILD_ROOT%{_bindir}/tzselect
%{__rm} $RPM_BUILD_ROOT%{_bindir}/zdump
%{__rm} $RPM_BUILD_ROOT%{_sbindir}/zic
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man3/newctime.3*
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man3/newtzset.3*
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man8/tzselect.8*
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man8/zdump.8*
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man8/zic.8*
%{__rm} $RPM_BUILD_ROOT%{_prefix}/lib/libtz.a
%{__rm} $RPM_BUILD_ROOT%{_datadir}/zoneinfo-posix
%{__rm} $RPM_BUILD_ROOT%{_datadir}/zoneinfo/leapseconds
%{__rm} $RPM_BUILD_ROOT%{_datadir}/zoneinfo/zone1970.tab
%{__mv} $RPM_BUILD_ROOT%{_datadir}/zoneinfo-leaps $RPM_BUILD_ROOT%{_datadir}/zoneinfo/right

%if %{with tests}
# test needs to be ran after "make install", as it uses installed files
: ====================TESTING=========================
%{__make} check \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} %{rpmldflags}"
: ====================TESTING END=====================
%endif

# behave more like glibc.spec
ln -sf %{_sysconfdir}/localtime	$RPM_BUILD_ROOT%{_datadir}/zoneinfo/localtime
ln -sf localtime $RPM_BUILD_ROOT%{_datadir}/zoneinfo/posixtime
ln -sf localtime $RPM_BUILD_ROOT%{_datadir}/zoneinfo/posixrules

# zic>=2020b installs localtime as hardlink to GMT, so remove first not break GMT zone files
%{__rm} $RPM_BUILD_ROOT/etc/localtime
> $RPM_BUILD_ROOT/etc/localtime

# header file
cp -p tzfile.h $RPM_BUILD_ROOT%{_includedir}/tzfile.h
cp -p tzfile.5 $RPM_BUILD_ROOT%{_mandir}/man5

install -p %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/timezone
cp -p %{SOURCE4} $RPM_BUILD_ROOT/etc/sysconfig/timezone
ln -s /dev/null $RPM_BUILD_ROOT%{systemdunitdir}/timezone.service

%if %{with java}
cp -a zoneinfo/java $RPM_BUILD_ROOT%{_datadir}/javazi
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add timezone
%service timezone restart

%preun
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del timezone

	# save for postun
	localtime=$(readlink -f /etc/localtime)
	# cp has no dereference target option, so remove link first
	test -L /etc/localtime.rpmsave && rm -f /etc/localtime.rpmsave
	cp -pf $localtime /etc/localtime.rpmsave
fi

%postun
if [ "$1" = "0" ]; then
	if [ ! -f /etc/localtime -a -f /etc/localtime.rpmsave ]; then
		echo >&2 "Preserving /etc/localtime"
		mv -f /etc/localtime{.rpmsave,}
	fi
fi

%triggerpostun -- rc-scripts < 0.4.1.4
/sbin/chkconfig --add timezone

%triggerpostun -- tzdata < 2015f-2
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
%systemd_service_disable timezone.service
%systemd_service_stop timezone.service

%files
%defattr(644,root,root,755)
%doc README tz-link.html
%ghost /etc/localtime
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/timezone
%attr(754,root,root) /etc/rc.d/init.d/timezone
%{systemdunitdir}/timezone.service
%{_datadir}/zoneinfo/localtime
%{_datadir}/zoneinfo/posixrules
%{_datadir}/zoneinfo/posixtime

%if %{with java}
%files -n java-tzdata
%defattr(644,root,root,755)
%{_datadir}/javazi
%endif

%files zoneinfo
%defattr(644,root,root,755)
%{_datadir}/zoneinfo
%exclude %{_datadir}/zoneinfo/right
%exclude %{_datadir}/zoneinfo/localtime
%exclude %{_datadir}/zoneinfo/posixrules
%exclude %{_datadir}/zoneinfo/posixtime

%files zoneinfo_right
%defattr(644,root,root,755)
%{_datadir}/zoneinfo/right

%files devel
%defattr(644,root,root,755)
%doc tzfile.5.txt
%{_includedir}/tzfile.h
%{_mandir}/man5/tzfile.5*
