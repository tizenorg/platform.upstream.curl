Name:           curl
Version:        7.32.0
Release:        0
License:        MIT
Summary:        A utility for getting files from remote servers (FTP, HTTP, and others)
Url:            http://curl.haxx.se/
Group:          Base/Utilities
Source0:        %{name}-%{version}.tar.bz2
Source1001:     %{name}.manifest
BuildRequires:  pkgconfig(libcares)
BuildRequires:  pkgconfig(libidn)
BuildRequires:  pkgconfig(nss)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(zlib)
Provides:       webclient

%description
cURL is a tool for getting files from HTTP, FTP, FILE, LDAP, LDAPS,
DICT, TELNET and TFTP servers, using any of the supported protocols.
cURL is designed to work without user interaction or any kind of
interactivity. cURL offers many useful capabilities, like proxy support,
user authentication, FTP upload, HTTP post, and file transfer resume.

%package -n libcurl
Summary:        A library for getting files from web servers
Group:          Base/Libraries

%description -n libcurl
This package provides a way for applications to use FTP, HTTP, Gopher and
other servers for getting files.

%package -n libcurl-devel
Summary:        Files needed for building applications with libcurl
Group:          Base/Development
Requires:       libcurl = %{version}
Requires:       libidn-devel
Provides:       curl-devel = %{version}
Obsoletes:      curl-devel < %{version}

%description -n libcurl-devel
cURL is a tool for getting files from FTP, HTTP, Gopher, Telnet, and
Dict servers, using any of the supported protocols. The libcurl-devel
package includes files needed for developing applications which can
use cURL's capabilities internally.

%prep
%setup -q
cp %{SOURCE1001} .

%build
export CPPFLAGS="$(pkg-config --cflags nss) -DHAVE_PK11_CREATEGENERICOBJECT"

%reconfigure --without-nss \
        --without-gnutls \
        --with-openssl \
        --disable-ipv6 \
        --with-ca-path=/etc/ssl/certs \
        --with-libidn \
        --with-lber-lib=lber \
        --enable-manual \
        --enable-versioned-symbols \
        --enable-ares \
        --enable-debug \
        --enable-curldebug \
        --disable-static

sed -i -e 's,-L/usr/lib ,,g;s,-L/usr/lib64 ,,g;s,-L/usr/lib$,,g;s,-L/usr/lib64$,,g' \
Makefile libcurl.pc

# Remove bogus rpath
sed -i \
-e 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' \
-e 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} INSTALL="install -p" install

rm -f %{buildroot}%{_libdir}/libcurl.la
install -d %{buildroot}/%{_datadir}/aclocal
install -m 644 docs/libcurl/libcurl.m4 %{buildroot}/%{_datadir}/aclocal

# don't need curl's copy of the certs; use openssl's
find %{buildroot} -name ca-bundle.crt -exec rm -f '{}' \;
rm -rf %{buildroot}%{_datadir}/man

%post -n libcurl -p /sbin/ldconfig

%postun -n libcurl -p /sbin/ldconfig

%files
%manifest %{name}.manifest
%license COPYING
%{_bindir}/curl

%files -n libcurl
%manifest %{name}.manifest
%license COPYING
%{_libdir}/libcurl.so.*

%files -n libcurl-devel
%manifest %{name}.manifest
%{_bindir}/curl-config*
%{_includedir}/curl
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc
%{_datadir}/aclocal/libcurl.m4
