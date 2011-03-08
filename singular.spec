%define		name		singular
%define		devname		%mklibname %{name} -d
%define		staticname	%mklibname %{name} -d -s
%define		singulardir	%{_datadir}/singular

Name:		%{name}
Summary:	Computer Algebra System for polynomial computations
Version:	3.1.1
Release:	%mkrel 3
License:	GPL
Group:		Sciences/Mathematics
Source0:	http://www.mathematik.uni-kl.de/ftp/pub/Math/Singular/SOURCES/3-1-1/Singular-3-1-1-4.tar.gz
Source1:	http://www.mathematik.uni-kl.de/ftp/pub/Math/Singular/Factory/factory-3-1-1.tar.gz
Source2:	http://www.mathematik.uni-kl.de/ftp/pub/Math/Singular/Factory/factory-doc.tar.gz
Source3:	http://www.mathematik.uni-kl.de/ftp/pub/Math/Singular/Libfac/libfac-3-1-1.tar.gz
Source4:	fix-singular-includes.pl
Source5:	singular.hlp
Source6:	singular.idx
URL:		http://www.singular.uni-kl.de/

BuildRequires:	libgmp-devel ntl-devel flex libncurses-devel readline-devel
Requires:	surf

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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
Provides:	%{name}-static-devel = %{version}-%{release}
Requires:	%{name}-devel = %{version}-%{release}

%description	-n %{staticname}
This package contains the Singular static libraries.

%prep
#%#setup -q -n Singular-3-1-1 -a1 -a2 -a3
%setup -q -n Singular-3-1-1

%build
find . -type d -name CVS -exec rm -fr {} \; 2> /dev/null || :

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
	--with-apint=gmp				\
	--with-gmp=%{_prefix}				\
	--with-ntl=%{_prefix}				\
	--with-NTL					\
	--without-MP					\
	--without-lex					\
	--without-bison					\
	--without-Boost					\
	--enable-factory				\
	--enable-libfac					\
	--enable-Singular				\
	--enable-IntegerProgramming			\
	--enable-Texinfo				\
	--enable-Texi2html				\
	--enable-doc					\
	--enable-emacs

perl -pi					\
	-e 's|(#define\s+HAVE_BOOST)|//$1|g;'	\
	`find . -name \*.h`

make

# need MP to build doc or will lock on failed tcp connection
#pushd doc
#    make SINGULAR=%{buildroot}%{singulardir}/%{arch}/Singular-3-1-1 all
#popd

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
rm -f Singular/Singular %{buildroot}%{_prefix}/Singular-3-1-1
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
	LLL Singular-3-1-1 solve_IP		\
	surfex toric_ideal TSingular		\
	*.so %{_lib}/*.o			\
	%{buildroot}%{singulardir}/%{_arch}
  rm -f LIB Singular

  pushd %{buildroot}%{_includedir}
    [ -d %{name} ] || mkdir %{name}
    mv -f *.c *.h templates %{name}
  popd
popd

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{singulardir}/LIB/gftables
cp -fa Singular/LIB/*.lib %{buildroot}%{singulardir}/LIB
cp -far Singular/LIB/gftables/* %{buildroot}%{singulardir}/LIB/gftables
cp -fa Singular/LIB/surfex/surfex.jar %{buildroot}%{singulardir}/LIB
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/Singular << EOF
#!/bin/sh

SINGULARPATH=%{singulardir}/LIB %{singulardir}/%{_arch}/Singular-3-1-1 \$*
EOF
chmod +x %{buildroot}%{_bindir}/Singular
ln -sf %{_bindir}/Singular %{buildroot}%{_bindir}/singular

perl -pi -e								\
	's|(java -jar) (surfex.jar)|$1 %{singulardir}/LIB/$2|;'		\
	%{buildroot}%{singulardir}/LIB/surfex

# these headers are included by installed ones, but not installed...
mkdir -p %{buildroot}%{_includedir}/%{name}/Singular
cp -fa Singular/*.h %{buildroot}%{_includedir}/%{name}/Singular

# correct includes
perl %{SOURCE4}

# keep only libsingular.h outside %{_includedir}/%{name}
mv %{buildroot}%{_includedir}/%{name}/libsingular.h %{buildroot}%{_includedir}
# files required during sagemath build, and/or side effect of sagemath patch
cp kernel/kInline.cc %{buildroot}%{_includedir}/%{name}
cp Singular/{attrib,grammar,ipid,ipshell,lists,subexpr,tok}.h  %{buildroot}%{_includedir}/%{name}

# installed headers are only readable by file owner...
chmod -R a+r %{buildroot}
find %{buildroot}%{_includedir} -type f -exec chmod a-x {} \;

# move conflicting static files to archdir
mv -f %{buildroot}%{_libdir}/*.a %{buildroot}%{singulardir}/%{_arch}

cp %{SOURCE5} %{SOURCE6} %{buildroot}%{singulardir}

rm -fr %{buildroot}%{_includedir}/NTL

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_bindir}/Singular
%{_bindir}/singular
%dir %{singulardir}
%dir %{singulardir}/%{_arch}
%{singulardir}/%{_arch}/ESingular
%{singulardir}/%{_arch}/LLL
%{singulardir}/%{_arch}/Singular-3-1-1
%{singulardir}/%{_arch}/TSingular
%{singulardir}/%{_arch}/change_cost
%{singulardir}/%{_arch}/gen_test
%{singulardir}/%{_arch}/libparse
%{singulardir}/%{_arch}/solve_IP
%{singulardir}/%{_arch}/surfex
%{singulardir}/%{_arch}/toric_ideal
%{singulardir}/LIB
%{singulardir}/singular.*

%files		-n %{devname}
%defattr(-,root,root)
%{singulardir}/%{_arch}/*.so
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*
%{_includedir}/*.h
%{_libdir}/*.so

%files		-n %{staticname}
%defattr(-,root,root)
%{singulardir}/%{_arch}/*.o
%{singulardir}/%{_arch}/*.a
