Summary:	Timezone data
Name:		tzdata
Version:	2005h
Release:	1
License:	GPL
Group:		System Environment/Base
Source0:	%{name}.tar.bz2
# Source0-md5:	d20ffc3a857fd1714daadf8edacfb37a
Source1:	%{name}%{version}.tar.gz
# Source1-md5:	4c7aa406b55cce53b268ad4d274f33ba
Source2:	tzcode%{version}.tar.gz
# Source2-md5:	cc4d27cfad7a8405fa198afbbd514204
BuildRequires:	gawk
BuildRequires:	glibc-devel
BuildRequires:	perl
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -n -u)

%description
This package contains data files with rules for various timezones around
the world.

%prep
%setup -n tzdata
mkdir %{name}%{version}
tar xzf %{SOURCE1} -C %{name}%{version}
mkdir tzcode%{version}
tar xzf %{SOURCE2} -C tzcode%{version}

%build
sed -e 's|@objpfx@|'`pwd`'/obj/|' \
    -e 's|@datadir@|%{_datadir}|' \
    -e 's|@install_root@|%{buildroot}|' \
  Makeconfig.in > Makeconfig
make
grep -v tz-art.htm tzcode%{version}/tz-link.htm > tzcode%{version}/tz-link.html

%install
make install
echo ====================TESTING=========================
make check
echo ====================TESTING END=====================

%clean
rm -rf %{buildroot}

%files
%defattr(644,root,root,755)
%{_datadir}/zoneinfo
%doc tzcode%{version}/README tzcode%{version}/Theory tzcode%{version}/tz-link.html
