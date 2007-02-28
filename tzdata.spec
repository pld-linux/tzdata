Summary:	Timezone data
Summary(pl):	Dane o strefach czasowych
Name:		tzdata
Version:	2007c
Release:	1
License:	GPL
Group:		Base
Source0:	%{name}-base-0.tar.bz2
# Source0-md5:	906a4c98cc5240f416524a256b039c42
Source1:	ftp://elsie.nci.nih.gov/pub/%{name}%{version}.tar.gz
# Source1-md5:	730d744ac691e950066f8b6bd17b02d0
Source2:	ftp://elsie.nci.nih.gov/pub/tzcode%{version}.tar.gz
# Source2-md5:	e4913aa2edaf097b0627ead6b45fbedc
Source3:	timezone.init
Source4:	timezone.sysconfig
BuildRequires:	gawk
BuildRequires:	perl-base
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts >= 0.4.1.4
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This package contains data files with rules for various timezones
around the world.

%description -l pl
Ten pakiet zawiera pliki z danymi na temat regu³ stref czasowych na
ca³ym ¶wiecie.

%package zoneinfo_right
Summary:	Non-POSIX (real) time zones
Summary(es):	Zonas de tiempo reales (no de POSIX)
Summary(pl):	Nie-POSIX-owe (prawdziwe) strefy czasowe
Group:		Libraries
Obsoletes:	glibc-zoneinfo_right

%description zoneinfo_right
You don't want this. Details at:
<http://sources.redhat.com/ml/libc-alpha/2000-12/msg00068.html>.

%description zoneinfo_right -l es
No lo necesita. Encontrará los detalles en:
<http://sources.redhat.com/ml/libc-alpha/2000-12/msg00068.html>.

%description zoneinfo_right -l pl
Nie potrzebujesz tego. Szczegó³y pod:
<http://sources.redhat.com/ml/libc-alpha/2000-12/msg00068.html>.

%prep
%setup -q -n %{name}
mkdir %{name}%{version}
%{__tar} xzf %{SOURCE1} -C %{name}%{version}
mkdir tzcode%{version}
%{__tar} xzf %{SOURCE2} -C tzcode%{version}

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

: ====================TESTING=========================
%{__make} check \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} %{rpmldflags}"
: ====================TESTING END=====================


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
fi

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
