#
# Conditional build
%bcond_without	tests			# make check
#
%define	tzdata_ver	2008b
%define	tzcode_ver	2008a
Summary:	Timezone data
Summary(pl.UTF-8):	Dane o strefach czasowych
Name:		tzdata
Version:	%{tzdata_ver}
Release:	2
License:	Public Domain (database), BSD/LGPL v2.1+ (code/test suite)
Group:		Base
Source0:	%{name}-base-0.tar.bz2
# Source0-md5:	906a4c98cc5240f416524a256b039c42
Source1:	ftp://elsie.nci.nih.gov/pub/%{name}%{tzdata_ver}.tar.gz
# Source1-md5:	dbeb9a327bbff77ab4078488b8c5323a
Source2:	ftp://elsie.nci.nih.gov/pub/tzcode%{tzcode_ver}.tar.gz
# Source2-md5:	4a04c12a8ec50b0a8cfc9ebce96b07d3
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
%setup -q -n %{name}
mkdir %{name}%{version}
%{__tar} xzf %{SOURCE1} -C %{name}%{version}
mkdir tzcode%{version}
%{__tar} xzf %{SOURCE2} -C tzcode%{version}
%patch0 -p1

sed -e "
s|@objpfx@|`pwd`/obj/|
s|@datadir@|%{_datadir}|
s|@install_root@|$RPM_BUILD_ROOT|
" Makeconfig.in > Makeconfig

grep -v tz-art.htm tzcode%{version}/tz-link.htm > tzcode%{version}/tz-link.html

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

%files
%defattr(644,root,root,755)
%doc tzcode%{version}/README tzcode%{version}/Theory tzcode%{version}/tz-link.html
%ghost /etc/localtime
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/timezone
%attr(754,root,root) /etc/rc.d/init.d/timezone

%{_datadir}/zoneinfo
%exclude %{_datadir}/zoneinfo/right

%files zoneinfo_right
%defattr(644,root,root,755)
%{_datadir}/zoneinfo/right
