Summary:	Timezone data
Summary(pl):	Dane o strefach czasowych
Name:		tzdata
Version:	2006c
Release:	1
License:	GPL
Group:		Base
Source0:	%{name}-base-0.tar.bz2
# Source0-md5:	906a4c98cc5240f416524a256b039c42
Source1:	ftp://elsie.nci.nih.gov/pub/%{name}%{version}.tar.gz
# Source1-md5:	420d97a09c9750839afc2703f6b8276f
Source2:	ftp://elsie.nci.nih.gov/pub/tzcode%{version}.tar.gz
# Source2-md5:	2100d0b0c6f2ad320260290e5dc7e957
BuildRequires:	gawk
BuildRequires:	perl-base
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This package contains data files with rules for various timezones
around the world.

%description -l pl
Ten pakiet zawiera pliki z danymi na temat regu³ stref czasowych na
ca³ym ¶wiecie.

%prep
%setup -q -n %{name}
mkdir %{name}%{version}
tar xzf %{SOURCE1} -C %{name}%{version}
mkdir tzcode%{version}
tar xzf %{SOURCE2} -C tzcode%{version}

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
%{__make} install
echo ====================TESTING=========================
%{__make} check
echo ====================TESTING END=====================

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc tzcode%{version}/README tzcode%{version}/Theory tzcode%{version}/tz-link.html
%{_datadir}/zoneinfo
