%define		php_name	php%{?php_suffix}
%define		modname		clamav
Summary:	Provides a interface to ClamAV for PHP
Name:		%{php_name}-%{modname}
Version:	0.15.7
Release:	1
License:	PHP License
Group:		Development/Languages/PHP
Source0:	http://downloads.sourceforge.net/php-clamav/php-clamav_%{version}.tar.gz
# Source0-md5:	7812fb38f75b76a212df335d18a72071
URL:		http://php-clamav.sourceforge.net/
BuildRequires:	%{php_name}-devel
BuildRequires:	clamav-devel
BuildRequires:	rpmbuild(macros) >= 1.666
%{?requires_php_extension}
Requires:	clamav
Provides:	php(%{modname}) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
PHP ClamaAV Lib is a PHP extension that allows to incorporate virus
scanning features in your PHP scripts. It uses the Clam Antivirus API
(libclamav) for virus scanning.

%prep
%setup -q -n php-clamav-%{version}

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
rm -rf $RPM_BUILD_ROOT
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

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc CHANGES CREDITS INSTALL phpclamav_test.php
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
