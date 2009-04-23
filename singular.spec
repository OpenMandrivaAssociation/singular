%define		name		singular
%define		libname		%mklibname %{name} 0
%define		devname		%mklibname %{name} -d
%define		staticname	%mklibname %{name} -d -s
%define		singulardir	%{_datadir}/singular

Name:		%{name}
Summary:	Computer Algebra System for polynomial computations
Version:	3.0.4
Release:	%mkrel 4
License:	GPL
Group:		Sciences/Mathematics
Source0:	http://www.mathematik.uni-kl.de/ftp/pub/Math/Singular/SOURCES/3-0-4/Singular-3-0-4-4.tar.gz
Source1:	http://www.mathematik.uni-kl.de/ftp/pub/Math/Singular/Factory/factory-3-1-0.tar.gz
Source2:	http://www.mathematik.uni-kl.de/ftp/pub/Math/Singular/Factory/factory-doc.tar.gz
Source3:	http://www.mathematik.uni-kl.de/ftp/pub/Math/Singular/Libfac/libfac-3-1-0.tar.gz
Source4:	fix-singular-includes.pl
URL:		http://www.singular.uni-kl.de/

BuildRequires:	libgmp-devel flex libncurses-devel readline-devel

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

Patch0:		Singular-3-0-4-4-Wformat.patch

%description
SINGULAR is a Computer Algebra system for polynomial computations with
special emphasize on the needs of commutative algebra, algebraic
geometry, singularity theory and polynomial system solving. For a more
detailed overview of SINGULAR, see
     http://www.singular.uni-kl.de/Overview/

%package	-n %{devname}
Group:		Development/Other
Summary:	Singular development files
Obsoletes:	%{name}-devel < 3.0.4-2
Provides:	%{name}-devel = %{version}-%{release}

%description	-n %{devname}
This package contains the Singular development files.

%package	-n %{staticname}
Group:		Development/Other
Summary:	Singular static libraries
Provides:	%{name}-devel-static = %{version}-%{release}
Requires:	%{name}-devel

%description	-n %{staticname}
This package contains the Singular static libraries.

%prep
%setup -q -n Singular-3-0-4 -a1 -a2 -a3

%patch0 -p1

%build
#   There is no way, other then patching all Makefiles.in by hand
# to make it respect DESTDIR ..., so build it pretending %{buildroot}
# is part of prefix, and correct the few wrong usages later.
#   It should be possible to build with proper --prefix, and use
# the install-sharedist target, but it will fail before, when trying
# to create directories in %{_prefix} during build.
export CXXFLAGS="%{optflags} -fPIC"
export CFLAGS="%{optflags} -fPIC"
./configure						\
	--prefix=%{buildroot}%{_prefix}			\
	--exec-prefix=%{buildroot}%{_prefix}		\
	--includedir=%{buildroot}%{_includedir}		\
	--libdir=%{buildroot}%{_libdir}			\
	--with-malloc=system				\
	--with-gmp=%{_prefix}				\
%ifarch %{ix86}
	--enable-MP					\
%endif
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

perl -pi					\
	-e 's|(#define\s+HAVE_BOOST)|//$1|g;'	\
	`find . -name \*.h`

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

# correct compilation by default without exceptions,
# but including c++ headers that generate exceptions
# (/usr/include/boost/dynamic_bitset/dynamic_bitset.hpp)
perl -i						\
	-e 's|--no-exceptions|-fexceptions|g;'	\
    `find . -name configure\*`

# these are not rebuilt after updating headers
rm -f Singular/Singular %{buildroot}%{_prefix}/Singular-3-0-4
# run make once more to recompile anything dependent on the patched headers.
make all libsingular

%install
%makeinstall_std install-libsingular

pushd %{buildroot}%{_prefix}
  pushd %{_lib}
    # these files are installed twice, due to the buildroot as prefix
    # in configure, as it wants to install files during normal build...
    rm -f dbmsr.so mpsr.so p_Procs_FieldGeneral.so	\
	p_Procs_FieldIndep.so p_Procs_FieldQ.so p_Procs_FieldZp.so
  popd
  mkdir -p %{buildroot}%{singulardir}/%{_arch}
  mv -f						\
	change_cost ESingular gen_test libparse	\
	LLL Singular-3-0-4 solve_IP		\
	surfex toric_ideal TSingular		\
	*.so *.sog %{_lib}/*.o			\
	%{buildroot}%{singulardir}/%{_arch}
  rm -f LIB Singular

  mkdir -p %{buildroot}%{_docdir}/%{name}-%{version}
  mv doc/* %{buildroot}%{_docdir}/%{name}-%{version}
  rm -fr doc
  ln -sf %{_docdir}/%{name}-%{version}  %{buildroot}%{singulardir}/doc 

  pushd %{buildroot}%{_includedir}
    [ -d %{name} ] || mkdir %{name}
    mv -f *.c *.h NTL templates %{name}
  popd
popd

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{singulardir}/LIB
cp -fa Singular/LIB/*.lib %{buildroot}%{singulardir}/LIB
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/Singular << EOF
#!/bin/sh

SINGULARPATH=%{singulardir}/LIB %{singulardir}/%{_arch}/Singular-3-0-4
EOF
chmod +x %{buildroot}%{_bindir}/Singular

# these headers are included by installed ones, but not installed...
mkdir -p %{buildroot}%{_includedir}/%{name}/Singular
cp -fa Singular/*.h %{buildroot}%{_includedir}/%{name}/Singular

# installed headers are only readable by file owner...
chmod -R a+r %{buildroot}
find %{buildroot}%{_includedir} -type f -exec chmod a-x {} \;

# correct includes
perl %{SOURCE4}

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
%{singulardir}/LIB

%files		-n %{devname}
%defattr(-,root,root)
%{singulardir}/%{_arch}/*.so
%{singulardir}/%{_arch}/*.sog
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*
%{_libdir}/*.so

%files		-n %{staticname}
%defattr(-,root,root)
%{singulardir}/%{_arch}/*.o
%{_libdir}/*.a
