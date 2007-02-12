Summary:	Timezone data
Summary(pl.UTF-8):   Dane o strefach czasowych
Name:		tzdata
Version:	2007a
Release:	2
License:	GPL
Group:		Base
Source0:	%{name}-base-0.tar.bz2
# Source0-md5:	906a4c98cc5240f416524a256b039c42
Source1:	ftp://elsie.nci.nih.gov/pub/%{name}%{version}.tar.gz
# Source1-md5:	5ba3a8c3581a0ef962179fba1328f3cb
Source2:	ftp://elsie.nci.nih.gov/pub/tzcode%{version}.tar.gz
# Source2-md5:	9162d8d447eec31f60d0602edd17e123
BuildRequires:	gawk
BuildRequires:	perl-base
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
Summary(es.UTF-8):   Zonas de tiempo reales (no de POSIX)
Summary(pl.UTF-8):   Nie-POSIX-owe (prawdziwe) strefy czasowe
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
install -d $RPM_BUILD_ROOT/etc/

%{__make} install

echo ====================TESTING=========================
%{__make} check \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} %{rpmldflags}"
echo ====================TESTING END=====================

# glibc.spec didn't keep it. so won't here either.
rm -rf $RPM_BUILD_ROOT%{_datadir}/zoneinfo/posix
# behave more like glibc.spec
ln -sf %{_sysconfdir}/localtime	$RPM_BUILD_ROOT%{_datadir}/zoneinfo/localtime
ln -sf localtime $RPM_BUILD_ROOT%{_datadir}/zoneinfo/posixtime
ln -sf localtime $RPM_BUILD_ROOT%{_datadir}/zoneinfo/posixrules

> $RPM_BUILD_ROOT/etc/localtime

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc tzcode%{version}/README tzcode%{version}/Theory tzcode%{version}/tz-link.html
%ghost /etc/localtime

%{_datadir}/zoneinfo
%exclude %{_datadir}/zoneinfo/right

%files zoneinfo_right
%defattr(644,root,root,755)
%{_datadir}/zoneinfo/right
