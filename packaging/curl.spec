Name:       curl
Summary:    A utility for getting files from remote servers (FTP, HTTP, and others)
Version:    7.48.0
Release:    1
Group:      Applications/Internet
License:    MIT
URL:        http://curl.haxx.se/
#Source0:    http://curl.haxx.se/download/%{name}-%{version}.tar.bz2
Source0:    %{name}-%{version}.tar.gz
Source1001:     %{name}.manifest

BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(libidn)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(libcares)
BuildRequires:	pkgconfig(libnghttp2)
Provides:   webclient


%description
curl is a client to get documents/files from servers, using any of the
supported protocols. The command is designed to work without user
interaction or any kind of interactivity.

curl offers a busload of useful tricks like proxy support, user
authentication, ftp upload, HTTP post, file transfer resume and more.

%package -n libcurl
Summary:    A library for getting files from web servers
Group:      System/Libraries
License:    MIT
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description -n libcurl
This package provides a way for applications to use FTP, HTTP, Gopher and
other servers for getting files.


%package -n libcurl-devel
Summary:    Files needed for building applications with libcurl
Group:      Development/Libraries
License:    MIT
Requires:   libcurl = %{version}-%{release}
Requires:   libidn-devel
Provides:   curl-devel = %{version}-%{release}
Obsoletes:   curl-devel < %{version}-%{release}

%description -n libcurl-devel
libcurl is the core engine of curl; this packages contains all the libs,
headers, and manual pages to develop applications using libcurl.

%prep
%setup -q
cp %{SOURCE1001} .

#%patch01 -p1
#%patch02 -p1

%build

export CPPFLAGS="-DHAVE_PK11_CREATEGENERICOBJECT"

%if "%{?profile}" == "tv"
CFLAGS+=" -DTIZEN_TV_EXT"
%reconfigure --without-nss --without-gnutls --with-openssl --disable-ipv6 \
%else
%reconfigure --without-nss --without-gnutls --with-openssl --enable-ipv6 \
%endif
--with-ca-path=/etc/ssl/certs \
--with-libidn \
--with-lber-lib=lber \
--enable-manual --enable-versioned-symbols --enable-ares --enable-debug --enable-curldebug \
--disable-static \
--with-nghttp2 \
--without-zsh-functions-dir \

#--with-ca-bundle=%{_sysconfdir}/pki/tls/certs/ca-bundle.crt 

sed -i -e 's,-L/usr/lib ,,g;s,-L/usr/lib64 ,,g;s,-L/usr/lib$,,g;s,-L/usr/lib64$,,g' \
Makefile libcurl.pc
# Remove bogus rpath
sed -i \
-e 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' \
-e 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags}

%install
rm -rf %{buildroot}

rm -rf $RPM_BUILD_ROOT

make DESTDIR=$RPM_BUILD_ROOT INSTALL="%{__install} -p" install

rm -f ${RPM_BUILD_ROOT}%{_libdir}/libcurl.la
install -d $RPM_BUILD_ROOT/%{_datadir}/aclocal
install -m 644 docs/libcurl/libcurl.m4 $RPM_BUILD_ROOT/%{_datadir}/aclocal


# don't need curl's copy of the certs; use openssl's
find ${RPM_BUILD_ROOT} -name ca-bundle.crt -exec rm -f '{}' \;
rm -rf ${RPM_BUILD_ROOT}/usr/share/man

# LICENSE
rm -rf %{buildroot}/usr/share/license
mkdir -p %{buildroot}/usr/share/license
cp COPYING %{buildroot}/usr/share/license/%{name}

%post -n libcurl -p /sbin/ldconfig

%postun -n libcurl -p /sbin/ldconfig

%files
%{_bindir}/curl

%files -n libcurl
%manifest %{name}.manifest
%{_libdir}/libcurl.so.*
/usr/share/license/%{name}

%files -n libcurl-devel
%{_bindir}/curl-config*
%{_includedir}/curl
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc
%{_datadir}/aclocal/libcurl.m4

