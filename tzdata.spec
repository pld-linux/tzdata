#
# Conditional build
%bcond_without	tests			# make check
#
%define		tzcode_ver	2008h
%define		tzdata_ver	2008h
Summary:	Timezone data
Summary(pl.UTF-8):	Dane o strefach czasowych
Name:		tzdata
Version:	%{tzdata_ver}
Release:	1
License:	Public Domain (database), BSD/LGPL v2.1+ (code/test suite)
Group:		Base
Source0:	%{name}-base-0.tar.bz2
# Source0-md5:	906a4c98cc5240f416524a256b039c42
Source1:	ftp://elsie.nci.nih.gov/pub/%{name}%{tzdata_ver}.tar.gz
# Source1-md5:	599dba784de0a560ba1a5ba1fdbb2082
Source2:	ftp://elsie.nci.nih.gov/pub/tzcode%{tzcode_ver}.tar.gz
# Source2-md5:	2f0fc8b1227bd7289483f64e8a194ed9
Source3:	timezone.init
Source4:	timezone.sysconfig
Patch0:		%{name}-test-update.patch
URL:		http://www.twinsun.com/tz/tz-link.htm
BuildRequires:	gawk
BuildRequires:	perl-base
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
Requires:	/sbin/chkconfig
Requires:	rc-scripts >= 0.4.1.4
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This package contains data files with rules for various timezones
around the world.

%description -l pl.UTF-8
Ten pakiet zawiera pliki z danymi na temat reguł stref czasowych na
całym świecie.

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

%prep
%setup -qc
mv tzdata/* .
%{__tar} xzf %{SOURCE1} -C tzdata
mkdir tzcode
%{__tar} xzf %{SOURCE2} -C tzcode
%patch0 -p1

sed -e "
s|@objpfx@|`pwd`/obj/|
s|@datadir@|%{_datadir}|
s|@install_root@|$RPM_BUILD_ROOT|
" Makeconfig.in > Makeconfig

grep -v tz-art.htm tzcode/tz-link.htm > tzcode/tz-link.html

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{sysconfig,rc.d/init.d}

%{__make} install

%if %{with tests}
: ====================TESTING=========================
%{__make} check \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} %{rpmldflags}"
: ====================TESTING END=====================
%endif


# glibc.spec didn't keep it. so won't here either.
rm -rf $RPM_BUILD_ROOT%{_datadir}/zoneinfo/posix
# behave more like glibc.spec
ln -sf %{_sysconfdir}/localtime	$RPM_BUILD_ROOT%{_datadir}/zoneinfo/localtime
ln -sf localtime $RPM_BUILD_ROOT%{_datadir}/zoneinfo/posixtime
ln -sf localtime $RPM_BUILD_ROOT%{_datadir}/zoneinfo/posixrules

> $RPM_BUILD_ROOT/etc/localtime

install %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/timezone
cp -a %{SOURCE4} $RPM_BUILD_ROOT/etc/sysconfig/timezone

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add timezone
%service timezone restart

%preun
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del timezone

	# save for postun
	cp -f /etc/localtime /etc/localtime.rpmsave
fi

%postun
if [ "$1" = "0" ]; then
	if [ ! -f /etc/localtime -a -f /etc/localtime.rpmsave ]; then
		mv -f /etc/localtime{.rpmsave,}
	fi
fi

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

%files
%defattr(644,root,root,755)
%doc tzcode/README tzcode/Theory tzcode/tz-link.html
%ghost /etc/localtime
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/timezone
%attr(754,root,root) /etc/rc.d/init.d/timezone

%{_datadir}/zoneinfo
%exclude %{_datadir}/zoneinfo/right

%files zoneinfo_right
%defattr(644,root,root,755)
%{_datadir}/zoneinfo/right
