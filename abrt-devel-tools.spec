%global commit a07dd2e97f9492c8e9d710a1f0787476ecf83d7e
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           abrt-devel-tools
Version:        1.0
Release:        1.git%{shortcommit}%{?dist}
Summary:        Universal screencasting frontend with pluggable support for various backends

Group:          Applications/System
License:        GPLv2+
URL:            https://github.com/mozeq/abrt-devel-tools
# this url is wrong, because github doesn't offer a space for downloadable archives :(
Source:         https://github.com/mozeq/abrt-devel-tools/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-setuptools

%description

%prep
%setup -qn %{name}-%{commit}

%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT

%check
%{__python} setup.py test


%files
%dir %{python_sitelib}/abrtdeveltools
%{python_sitelib}/abrtdeveltools/*.py*
# abrt-devel-tools-1.0-py2.7.egg-info
%dir %{python_sitelib}/abrt_devel_tools-%{version}-py2.7.egg-info
%{python_sitelib}/abrt_devel_tools-%{version}-py2.7.egg-info/*
%{_bindir}/submit-patch

%changelog
* Mon Sep 16 2013 Jiri Moskovcak <jmoskovc@redhat.com> 1.0-1
- initial rpm
