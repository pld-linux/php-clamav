%define		php_name	php%{?php_suffix}
%define		modname		clamav
Summary:	Provides a interface to ClamAV for PHP
Name:		%{php_name}-%{modname}
Version:	0.13
Release:	0.1
License:	PHP License
Group:		Development/Languages/PHP
Source0:	php-clamavlib-%{version}.tar.gz
# Source0-md5:	5ccb9daa8ed4181a9fafae5dd9297395
Patch0:		php-clamavlib-clamav-0.93_build_fix.diff
Patch1:		php-clamavlib-clamav-0.94_build_fix.diff
URL:		http://phpclamavlib.org/
BuildRequires:	clamav-devel
BuildRequires:	%{php_name}-devel
BuildRequires:	rpmbuild(macros) >= 1.666
%{?requires_php_extension}
Provides:	php(MODULE_NAME) = %{version}
Requires:	clamav
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
PHP ClamaAV Lib is a PHP extension that allows to incorporate virus
scanning features in your PHP scripts. It uses the Clam Antivirus API
(libclamav) for virus scanning.

%prep
%setup -q -n php-clamavlib-%{version}
%patch0 -p0
%patch1 -p0

%build
phpize
%configure
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_EXECUTABLE=%{__php}
%endif

%install
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so

[clamav]
clamav.dbpath="/var/lib/clamav"
clamav.maxreclevel=0
clamav.maxfiles=0
clamav.archivememlim=0
clamav.maxfilesize=0
EOF

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc CHANGES CREDITS EXPERIMENTAL INSTALL clamav.php
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
