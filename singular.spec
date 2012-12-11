%define		name			singular
%define		old_libsingular_devel	%mklibname %{name} -d
%define		old_libsingular_static	%mklibname %{name} -d -s
%define		singulardir		%{_libdir}/Singular

Name:		%{name}
Summary:	Computer Algebra System for polynomial computations
Version:	3.1.5
Release:	5
License:	BSD and LGPLv2+ and GPLv2+
Group:		Sciences/Mathematics
Source0:	http://www.mathematik.uni-kl.de/ftp/pub/Math/Singular/SOURCES/3-1-5/Singular-3-1-5.tar.gz
Source1:	singular.hlp
Source2:	singular.idx
URL:		http://www.singular.uni-kl.de/
BuildRequires:	emacs
BuildRequires:	flex
BuildRequires:	gmp-devel
BuildRequires:	ncurses-devel
BuildRequires:	ntl-devel
BuildRequires:	readline-devel
BuildRequires:	sharutils
BuildRequires:	texinfo
BuildRequires:	texlive
Requires:	surf

# Use destdir in install targets
Patch1:		Singular-destdir.patch
# Find headers in source tree
Patch2:		Singular-headers.patch
# Find and link to generated libraries
Patch3:		Singular-link.patch
# Do not attempt to load non existing modules, do not even run
# the binary in DESTDIR when building the documentation
Patch4:		Singular-doc.patch
# Correct koji error:
# ** ERROR: No build ID note found in /builddir/build/BUILDROOT/Singular-3.1.3-1.fc16.x86_64/usr/lib64/Singular/dbmsr.so
Patch5:		Singular-builddid.patch
# Correct undefined symbol in libsingular
# This patch removes a hack to avoid duplicated symbols in tesths.cc
# when calling mp_set_memory_functions, what is a really a bad idea on
# a shared library.
Patch6:		Singular-undefined.patch

# From sagemath singular-3-1-5.p0.spkg in "Upgrade Singular" trac
# at http://trac.sagemath.org/sage_trac/ticket/13237
Patch7:		NTL_negate.patch
Patch8:		singular_trac_439.patch
Patch9:		singular_trac_440.patch
Patch10:	singular_trac_441.patch

## Macaulay2 patches
Patch20: Singular-M2_factory.patch
Patch21: Singular-M2_memutil_debuggging.patch
Patch22: Singular-M2_libfac.patch

%description
Singular is a computer algebra system for polynomial computations, with
special emphasis on commutative and non-commutative algebra, algebraic
geometry, and singularity theory. It is free and open-source under the
GNU General Public Licence.

%package	devel
Group:		Development/Other
Summary:	Singular development files
Obsoletes:	%{old_libsingular_devel} < %{version}-%{release}
Obsoletes:	%{old_libsingular_static} < %{version}-%{release}
Provides:	%{old_libsingular_devel} = %{version}-%{release}

%description	devel
This package contains the Singular development files.

%package	-n factory-devel
Summary:	C++ class library for multivariate polynomial data
Group:		Development/Other
Requires:	gmp-devel
Obsoletes:	factory-static < %{version}-%{release}
Provides:	factory-static = %{version}-%{release}

%description	-n factory-devel 
Factory is a C++ class library that implements a recursive representation
of multivariate polynomial data.

%package	-n libfac-devel
Summary:	An extension to Singular-factory
Group:		Development/Other
Obsoletes:	libfac-static < %{version}-%{release}
Provides:	libfac-static = %{version}-%{release}

%description	-n libfac-devel
Singular-libfac is an extension to Singular-factory which implements
factorization of polynomials over finite fields and algorithms for
manipulation of polynomial ideals via the characteristic set methods
(e.g., calculating the characteristic set and the irreducible
characteristic series).

%package	examples
Summary:	Singular example files
Group:		Sciences/Mathematics
Requires:	%{name} = %{version}-%{release}

%description	examples
This package contains the Singular example files.

%package	doc
Summary:	Singular documentation files
Group:		Sciences/Mathematics
Requires:	%{name} = %{version}-%{release}

%description	doc
This package contains the Singular documentation files.

%package	surfex
Summary:	Singular java interface
Group:		Sciences/Mathematics
Requires:	java
Requires:	%{name} = %{version}-%{release}

%description	surfex
This package contains the Singular java interface.

%package	emacs
Summary:	Emacs mode for Singular
Group:		Sciences/Mathematics
Requires:	emacs-common
Requires:	%{name} = %{version}-%{release}

%description	emacs
Emacs mode for Singular.

%prep
%setup -q -n Singular-3-1-5
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1

%patch20 -p1 -b .M2_factory
%patch21 -p1 -b .M2_memutil_debuggging
%patch22 -p1 -b .M2_libfac

sed -i -e "s|gftabledir=.*|gftabledir='%{singulardir}/LIB/gftables'|"	\
    -e "s|explicit_gftabledir=.*|explicit_gftabledir='%{singulardir}/LIB/gftables'|" \
    factory/configure.in

# Force use of system ntl
rm -fr ntl

%build
export CFLAGS="%{optflags} -fPIC"
export CXXFLAGS=$CFLAGS

# build components in specific order to not need to build & install
# in a single make command
%configure \
	--bindir=%{singulardir} \
	--with-apint=gmp \
	--with-gmp=%{_prefix} \
	--with-ntl=%{_prefix} \
	--with-NTL \
	--without-MP \
	--without-lex \
	--without-bison \
	--without-Boost \
	--enable-gmp=%{_prefix} \
	--enable-Singular \
	--enable-factory \
	--enable-libfac \
	--enable-IntegerProgramming \
	--disable-doc \
	--with-malloc=system
# remove bogus -L/usr/kernel from linker command line and
# do not put standard library in linker command line to avoid
# linking with a system wide libsingcf or libfacf
sed -i 's|-L%{_prefix}/kernel||g;s|-L%{_libdir}||g' Singular/Makefile
make %{?_smp_mflags} Singular
# factory needs omalloc built
make %{?_smp_mflags} -C omalloc

pushd factory
%configure \
	--bindir=%{singulardir} \
	--includedir=%{_includedir}/factory \
	--with-apint=gmp \
	--with-gmp=%{_prefix} \
	--with-ntl=%{_prefix} \
	--with-NTL \
	--with-Singular \
	--enable-gmp=%{_prefix}
    make %{?_smp_mflags}
popd

# kernel needs factory built
make %{?_smp_mflags} -C kernel

# libfac needs factory built
pushd libfac
%configure \
	--bindir=%{singulardir} \
	--with-apint=gmp \
	--with-gmp=%{_prefix} \
	--with-ntl=%{_prefix} \
	--with-NTL \
	--enable-factory \
	--enable-libfac \
	--enable-omalloc \
	--enable-gmp=%{_prefix}
    make %{?_smp_mflags}
    # not built by default
    make libfac.a
popd

# target required to rebuild documentation
make %{?_smp_mflags} -C Singular libparse

%install
make \
	DESTDIR=$RPM_BUILD_ROOT \
	install_prefix=$RPM_BUILD_ROOT%{singulardir} \
	slibdir=%{singulardir}/LIB \
	install \
	install-libsingular \
	install-sharedist

# does not need to be in top directory
mv $RPM_BUILD_ROOT%{_includedir}/{my,om}limits.h \
    $RPM_BUILD_ROOT%{_includedir}/singular

# also installed in libdir
rm -f $RPM_BUILD_ROOT%{_bindir}/*.so
rm -f $RPM_BUILD_ROOT%{singulardir}/libsingular.so

# already linked to libsingular.so; do not distribute static libraries
# or just compiled objects.
rm -f $RPM_BUILD_ROOT%{_libdir}/*.a $RPM_BUILD_ROOT%{_libdir}/*.o

# avoid poluting libdir with dynamic modules
pushd $RPM_BUILD_ROOT%{_libdir}
    mkdir -p Singular
    mv dbmsr.so p_Procs*.so Singular
popd

# create a script also setting SINGULARPATH
mkdir -p $RPM_BUILD_ROOT%{_bindir}
cat > $RPM_BUILD_ROOT%{_bindir}/Singular << EOF
#!/bin/sh

SINGULARPATH=%{singulardir} %{singulardir}/Singular-3-1-5 "\$@"
EOF
chmod +x $RPM_BUILD_ROOT%{_bindir}/Singular

# TSingular
cat > $RPM_BUILD_ROOT%{_bindir}/TSingular << EOF
#!/bin/sh

%{singulardir}/TSingular --singular %{_bindir}/Singular "\$@"
EOF
chmod +x $RPM_BUILD_ROOT%{_bindir}/TSingular

# remove some wrong executable permissions
chmod 644 $RPM_BUILD_ROOT%{singulardir}/LIB/*.lib

# surfex
cat > $RPM_BUILD_ROOT%{_bindir}/surfex << EOF
#!/bin/sh

%{singulardir}/surfex %{singulardir}/LIB/surfex "\$@"
EOF
chmod +x $RPM_BUILD_ROOT%{_bindir}/surfex
mkdir -p $RPM_BUILD_ROOT%{singulardir}/LIB/surfex/doc
install -m644 Singular/LIB/surfex/doc/surfex_doc_linux.pdf \
    $RPM_BUILD_ROOT%{singulardir}/LIB/surfex/doc/surfex_doc_linux.pdf

# referenced in xemacs setup
install -m644 emacs/singular.xpm $RPM_BUILD_ROOT%{_lispdir}/singular

# remove suggested preferences
rm -f $RPM_BUILD_ROOT%{_lispdir}/singular/.emacs-general

# emacs autostart
sed -i "s|<your-singular-emacs-home-directory>|%{_ispdir}/singular|" \
    $RPM_BUILD_ROOT%{_lispdir}/singular/.emacs-singular
mv $RPM_BUILD_ROOT%{_lispdir}/singular/.emacs-singular \
     $RPM_BUILD_ROOT%{_lispdir}/singular-init.el

# ESingular
cat > $RPM_BUILD_ROOT%{_bindir}/ESingular << EOF
#!/bin/sh

export ESINGULAR_EMACS_LOAD=%{_emacs_sitestartdir}/singular-init.el
export ESINGULAR_EMACS_DIR=%{_lispdir}/singular
%{singulardir}/ESingular --singular %{_bindir}/Singular "\$@"
EOF
chmod +x $RPM_BUILD_ROOT%{_bindir}/ESingular

pushd libfac
    make DESTDIR=$RPM_BUILD_ROOT install
    # not installed by default
    install -m 644 libfac.a $RPM_BUILD_ROOT%{_libdir}/libfac.a
popd

pushd factory
    make DESTDIR=$RPM_BUILD_ROOT install
# make a version without singular defined
    make clean
%configure \
	--bindir=%{singulardir} \
	--includedir=%{_includedir}/factory \
	--with-apint=gmp \
	--with-gmp=%{_prefix} \
	--with-ntl=%{_prefix} \
	--with-NTL \
	--without-Singular \
	--enable-gmp=%{_prefix}
    # avoid missing "print" symbols not used elsewhere
    make CPPFLAGS="-DNOSTREAMIO=1" %{?_smp_mflags}
    # not built by default
    make libcfmem.a
    # do not run make install again, just install non singular factory files
    install -m 644 libcf.a $RPM_BUILD_ROOT%{_libdir}
    install -m 644 libcfmem.a $RPM_BUILD_ROOT%{_libdir}
    # automatically generated file at install time ignores includedir
    sed	-e 's|<factory|<factory/factory|' \
	-e 's|<templates/|<factory/templates/|' \
	-i $RPM_BUILD_ROOT%{_includedir}/factory/templates/ftmpl_inst.cc
popd
sed -e 's|<\(cf_gmp.h>\)|<factory/\1|' \
    -i $RPM_BUILD_ROOT%{_includedir}/singular/si_gmp.h

%files
%{_bindir}/Singular
%{_bindir}/TSingular
%doc %{singulardir}/COPYING
%doc %{singulardir}/GPL2
%doc %{singulardir}/GPL3
%doc %{singulardir}/NEWS
%doc %{singulardir}/README
%dir %{singulardir}
%dir %{singulardir}/LIB
%doc %{singulardir}/LIB/COPYING
%{singulardir}/LIB/*.lib
%{singulardir}/LIB/help.cnf
%{singulardir}/LIB/gftables
%{singulardir}/doc
%{singulardir}/info
%{singulardir}/change_cost
%{singulardir}/gen_test
%{singulardir}/libparse
%{singulardir}/LLL
%{singulardir}/Singular*
%{singulardir}/solve_IP
%{singulardir}/toric_ideal
%{singulardir}/TSingular
%{singulardir}/*.so
%{_libdir}/libsingular.so

%files		devel
%{_includedir}/libsingular.h
%{_includedir}/omalloc.h
%{_includedir}/singular

%files		-n factory-devel
%doc factory/ChangeLog
%doc factory/NEWS
%doc factory/README
%{_includedir}/factory
%{_libdir}/libcf.a
%{_libdir}/libcfmem.a
%{_libdir}/libsingcf*.a

%files		-n libfac-devel
%doc libfac/00README
%doc libfac/ChangeLog
%doc libfac/COPYING
%{_includedir}/factor.h
%{_libdir}/libfac.a
%{_libdir}/libsingfac*.a

%files		examples
%{singulardir}/examples

%files		doc
%doc %{singulardir}/html
%doc %{singulardir}/*.html

%files		surfex
%{_bindir}/surfex
%{singulardir}/surfex
%{singulardir}/LIB/surfex

%files		emacs
%{_bindir}/ESingular
%{singulardir}/ESingular
%{_lispdir}/singular
%{_lispdir}/singular-init.el


%changelog
* Tue Aug 28 2012 Paulo Andrade <pcpa@mandriva.com.br> 3.1.5-5
+ Revision: 815910
- Rebuild.

* Mon Aug 20 2012 Paulo Andrade <pcpa@mandriva.com.br> 3.1.5-4
+ Revision: 815493
- Correct wrong include path for a factory-devel file.

* Wed Aug 15 2012 Paulo Andrade <pcpa@mandriva.com.br> 3.1.5-3
+ Revision: 814892
- Rebuild to address build system issues.
- Bump release and rebuild due to buildsystem problems.
- Update to release matching http://pkgs.fedoraproject.org/cgit/Singular.git

* Sat Nov 05 2011 Paulo Andrade <pcpa@mandriva.com.br> 3.1.3-3
+ Revision: 720010
- Fix build and sagemath 4.7.2 linkage.

* Sat Nov 05 2011 Paulo Andrade <pcpa@mandriva.com.br> 3.1.3-2
+ Revision: 719032
- Correct factory include and path.

* Sat Nov 05 2011 Paulo Andrade <pcpa@mandriva.com.br> 3.1.3-1
+ Revision: 718731
- Update to Singular-3-1-3

* Wed Jun 01 2011 Paulo Andrade <pcpa@mandriva.com.br> 3.1.1-4
+ Revision: 682293
- Rebuild ensuring it does not use its local modified copy of ntl

* Tue Mar 08 2011 Paulo Andrade <pcpa@mandriva.com.br> 3.1.1-3
+ Revision: 642824
- Rebuild singular with its local/modified ntl build

* Thu Sep 23 2010 Paulo Andrade <pcpa@mandriva.com.br> 3.1.1-2mdv2011.0
+ Revision: 580795
- Update prebuilt documentation files to match singular version

* Wed Sep 22 2010 Paulo Andrade <pcpa@mandriva.com.br> 3.1.1-1mdv2011.0
+ Revision: 580442
- Update to Singular 3.1.1

* Thu Feb 11 2010 Paulo Andrade <pcpa@mandriva.com.br> 3.1.0-14mdv2010.1
+ Revision: 504285
- Update for build of sagemath 4.3.2

* Wed Feb 10 2010 Funda Wang <fwang@mandriva.org> 3.1.0-13mdv2010.1
+ Revision: 503620
- rebuild for new gmp

* Mon Jan 04 2010 Paulo Andrade <pcpa@mandriva.com.br> 3.1.0-12mdv2010.1
+ Revision: 486264
+ rebuild (emptylog)

* Wed Nov 18 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.1.0-10mdv2010.1
+ Revision: 467282
+ rebuild (emptylog)

* Tue Nov 17 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.1.0-9mdv2010.1
+ Revision: 467051
- Add documentation files and correct sage 4.2 crash

* Tue Nov 17 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.1.0-8mdv2010.1
+ Revision: 466703
- Update for sage 4.2 build.

* Thu Sep 10 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.1.0-7mdv2010.0
+ Revision: 436224
- disable build of alternate libntl

* Fri Sep 04 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.1.0-6mdv2010.0
+ Revision: 431798
- Add minor patch to match sagemath doctest expected results
- add a lowercase symlink to /usr/bin/Singular

* Mon Aug 31 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.1.0-5mdv2010.0
+ Revision: 423079
- Install .a libraries in the singular archdir, to avoid conflicts with ntl.

* Fri Aug 14 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.1.0-4mdv2010.0
+ Revision: 416241
+ rebuild (emptylog)

* Thu Aug 13 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.1.0-3mdv2010.0
+ Revision: 416218
- Correct Singular shell script to actually pass command line arguments
- Install surfex.jar and patch surfex to find it

* Wed Jul 15 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.1.0-2mdv2010.0
+ Revision: 396452
+ rebuild (emptylog)

* Wed Jul 15 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.1.0-1mdv2010.0
+ Revision: 396445
- Update to latest upstream release version 3.1.0, patchlevel 4.

* Fri May 29 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.0.4-7mdv2010.0
+ Revision: 381167
- Correct memory corruptions problems in sagemath, that had it's root
  cause in the singular package.

* Mon May 18 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.0.4-6mdv2010.0
+ Revision: 377388
+ rebuild (emptylog)

* Fri May 08 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.0.4-5mdv2010.0
+ Revision: 373545
+ rebuild (emptylog)

* Thu Apr 23 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.0.4-4mdv2009.1
+ Revision: 368954
- Install .lib files, as the Singular binary wants to read them.

* Thu Apr 16 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.0.4-3mdv2009.1
+ Revision: 367788
- Correct include path to work from %%{_includedir}, and "manually" install
  headers that are required by the ones that are installed by %%makeinstall_std.

* Tue Apr 07 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.0.4-2mdv2009.1
+ Revision: 365063
- o Compile C and C++ source with -fPIC to avoid x86_64 link problems.
  o Explicitly disable detection of libboost, as it generates link errors.
- o Renames singular-devel to libsingular-devel and add libsingular-static-devel.
  o Add missing files due to not executing 'make install-libsingular' target.

* Tue Mar 03 2009 Paulo Andrade <pcpa@mandriva.com.br> 3.0.4-1mdv2009.1
+ Revision: 348176
- Module MP wants sizeof(long) == 4. Disable build on x86_64.
- Initial import of singular, version 3.0.4.
  Singular is a Computer Algebra System for polynomial computations.
- singular

