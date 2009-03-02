%define		singulardir	%{_datadir}/singular

Name:		singular
Summary:	Computer Algebra System for polynomial computations
Version:	3.0.4
Release:	%mkrel 1
License:	GPL
Group:		Sciences/Mathematics
Source0:	http://www.mathematik.uni-kl.de/ftp/pub/Math/Singular/SOURCES/3-0-4/Singular-3-0-4-4.tar.gz
Source1:	http://www.mathematik.uni-kl.de/ftp/pub/Math/Singular/Factory/factory-3-1-0.tar.gz
Source2:	http://www.mathematik.uni-kl.de/ftp/pub/Math/Singular/Factory/factory-doc.tar.gz
Source3:	http://www.mathematik.uni-kl.de/ftp/pub/Math/Singular/Libfac/libfac-3-1-0.tar.gz
URL:		http://www.singular.uni-kl.de/

BuildRequires:	libgmp-devel

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
SINGULAR is a Computer Algebra system for polynomial computations with
special emphasize on the needs of commutative algebra, algebraic
geometry, singularity theory and polynomial system solving. For a more
detailed overview of SINGULAR, see
     http://www.singular.uni-kl.de/Overview/

%package	devel
Group:		Development/Other
Summary:	Singular development files
Requires:	%{name}

%description	devel
This package contains the Singular development files.

%prep
%setup -q -n Singular-3-0-4 -a1 -a2 -a3

%build
#   There is no way, other then patching all Makefiles.in by hand
# to make it respect DESTDIR ..., so build it pretending %{buildroot}
# is part of prefix, and correct the few wrong usages later.
#   It should be possible to build with proper --prefix, and use
# the install-sharedist target, but it will fail before, when trying
# to create directories in %{_prefix} during build.
./configure						\
	--prefix=%{buildroot}%{_prefix}			\
	--exec-prefix=%{buildroot}%{_prefix}		\
	--includedir=%{buildroot}%{_includedir}/%{name}	\
	--with-malloc=system				\
	--with-gmp=%{_prefix}				\
	--enable-MP					\
	--enable-factory				\
	--enable-libfac					\
	--enable-Singular				\
	--enable-IntegerProgramming			\
	--enable-Plural					\
	--enable-Texinfo				\
	--enable-Texi2html				\
	--enable-doc					\
	--enable-emacs
# --enable-sgroup
#	needs sgroup directory (tarball where?)

make
perl -pi					\
	-e 's|%{buildroot}||g;'			\
	-e 's|--with-external-config[^ ]+||g;'	\
	-e "s|\s*--cache-file[^']+||;"		\
	-e 's|in %{builddir}[^"]+||g;'		\
    kernel/mod2.h				\
    Singular/mod2.h				\
    factory/factoryconf.h			\
    factory/config.h

# these are not rebuilt after updating headers
rm -f Singular/Singular %{buildroot}%{_prefix}/Singular-3-0-4
# run make once more to recompile anything dependent on the patched headers.
make

%install
%makeinstall_std

pushd %{buildroot}%{_prefix}
  mkdir -p %{buildroot}%{singulardir}/%{_arch}
  mv -f						\
	change_cost ESingular gen_test libparse	\
	LLL Singular-3-0-4 solve_IP		\
	surfex toric_ideal TSingular		\
	*.so *.sog				\
	%{buildroot}%{singulardir}/%{_arch}
  rm -f LIB Singular

  mkdir -p %{buildroot}%{_docdir}/%{name}-%{version}
  mv doc/* %{buildroot}%{_docdir}/%{name}-%{version}
  rm -fr doc
  ln -sf %{_docdir}/%{name}-%{version}  %{buildroot}%{singulardir}/doc 
popd

mkdir -p %{buildroot}%{_bindir}
ln -sf %{singulardir}/%{_arch}/Singular-3-0-4 %{buildroot}%{_bindir}/Singular

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_bindir}/Singular
%doc %dir %{_docdir}/%{name}-%{version}
%doc %{_docdir}/%{name}-%{version}/*
%dir %{singulardir}
%{singulardir}/doc
%dir %{singulardir}/%{_arch}
%{singulardir}/%{_arch}/ESingular
%{singulardir}/%{_arch}/LLL
%{singulardir}/%{_arch}/Singular-3-0-4
%{singulardir}/%{_arch}/TSingular
%{singulardir}/%{_arch}/change_cost
%{singulardir}/%{_arch}/gen_test
%{singulardir}/%{_arch}/libparse
%{singulardir}/%{_arch}/solve_IP
%{singulardir}/%{_arch}/surfex
%{singulardir}/%{_arch}/toric_ideal

%files		devel
%defattr(-,root,root)
%{singulardir}/%{_arch}/*.so
%{singulardir}/%{_arch}/*.sog
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*
%{_libdir}/*.a
%{_libdir}/*.o
