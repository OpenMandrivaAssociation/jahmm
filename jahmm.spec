# Copyright (c) 2000-2008, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define gcj_support 1

Name:           jahmm
Version:        0.6.1
Release:        %mkrel 0.0.1
Epoch:          0
Summary:        Java implementation of Hidden Markov Model (HMM) related algorithms
License:        GPLv2+
Group:          Development/Java
URL:            http://www.run.montefiore.ulg.ac.be/~francois/software/jahmm/
Source0:        http://www.run.montefiore.ulg.ac.be/~francois/software/jahmm/files/jahmm-%{version}.tar.gz
Source1:        %{name}-%{version}.pom
Source2:        %{name}-desktop.desktop
Source3:        http://www.run.montefiore.ulg.ac.be/~francois/software/jahmm/doc/userguide/0.6.1/jahmm-userguide-0.6.1-src.tar.gz
Patch0:         %{name}-0.6.1-build.patch
Requires:       jpackage-utils >= 0:1.7.2
BuildRequires:  ant
BuildRequires:  ant-junit
%if %{gcj_support}
Requires(post): java-gcj-compat
Requires(postun): java-gcj-compat
BuildRequires:  java-gcj-compat-devel
%else
Buildarch:      noarch
%endif
BuildRequires:  java-rpmbuild
BuildRequires:  junit
BuildRequires:  dblatex
BuildRequires:  docbook-dtd-mathml20
BuildRequires:  docbook-dtd44-xml
BuildRequires:  docbook-style-xsl
BuildRequires:  libxslt-proc
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
Jahmm (pronounced "jam") is a Java implementation of Hidden Markov Model (HMM)
related algorithms. It's been designed to be easy to use (e.g. simple things
are simple to program) and general purpose. As it is licenced under GPL; its
source code is thus freely available.

This library is reasonably efficient, meaning that the complexity of the
implementation of the algorithms involved is that given by the theory. However,
when a choice must be made between code readability and efficiency, readability
has been chosen. It is thus ideal in research (because algorithms can easily be
modified) and as an academic tool (students can quickly get interesting
results).

Various algorithms are included in the latest version..

The library also provides a graphical user interface and a command-line
interface.

%package manual
Summary:        Manual for %{name}
Group:          Development/Java

%description manual
Documentation for %{name}.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
Javadoc for %{name}.

%package demo
Summary:        Demo for %{name}
Group:          Development/Java
AutoReqProv:    no
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       /usr/bin/env

%description demo
Demonstrations and samples for %{name}.

%prep
%setup -q 
%setup -q -T -D -a 3
%patch0 -p1
pushd user_guide
%{__perl} -pi -e 's|/usr/share/xml/docbook/stylesheet/nwalsh/|%{_datadir}/sgml/docbook/xsl-stylesheets-'$(rpm -q --queryformat "%{VERSION}" docbook-style-xsl)'/|' src/html.xsl src/xhtml.xsl
%{__perl} -pi -e 's|http://www.oasis-open.org/docbook/xml/4.4/docbookx.dtd|%{_datadir}/sgml/docbook/xml-dtd-4.4/docbookx.dtd|' src/*.xml
%{__perl} -pi -e 's|http://www.w3.org/TR/MathML2/dtd/mathml2.dtd|%{_datadir}/sgml/docbook/mathml20-dtd-20030619/mathml2.dtd|' src/examples.xml src/examples_vectors.mml
popd

%build
export OPT_JAR_LIST=:
export CLASSPATH=$(build-classpath junit)
%{ant} jar javadoc

export OPT_JAR_LIST="ant/ant-junit junit"
export CLASSPATH=`pwd`/build/lib/jahmm-0.6.1.jar
%{ant} junit
%{ant} test

pushd user_guide
make %{?_smp_mflags}
popd

%install
%{__rm} -rf %{buildroot}

# jars
%{__mkdir_p} %{buildroot}%{_javadir}
%{__cp} -a build/lib/%{name}-%{version}.jar \
  %{buildroot}%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do \
  %{__ln_s} ${jar} ${jar/-%{version}/}; done)

%add_to_maven_depmap %{name} %{name} %{version} JPP %{name}

# poms
%{__mkdir_p} %{buildroot}%{_datadir}/maven2/poms
%{__cp} -a %{SOURCE1} \
  %{buildroot}%{_datadir}/maven2/poms/JPP.%{name}.pom

# manual

# javadoc
%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__cp} -a javadoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__ln_s} %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

# demo
%{__mkdir_p} %{buildroot}%{_datadir}/%{name}
%{__cp} -a resources/* %{buildroot}%{_datadir}/%{name}
%{__chmod} 0755 %{buildroot}%{_datadir}/%{name}/*.sh

# scripts
%{__mkdir_p} %{buildroot}%{_bindir}

function jahmm_script() {
%{__cat} > %{buildroot}%{_bindir}/$1 << EOF
#!/bin/sh
#
# $1 script
# JPackage Project <http://www.jpackage.org/>

# Source functions library
. %{_datadir}/java-utils/java-functions

# Source system prefs
if [ -f %{_sysconfdir}/%{name}.conf ] ; then
  . %{_sysconfdir}/%{name}.conf
fi

# Source user prefs
if [ -f \$HOME/.%{name}rc ] ; then
  . \$HOME/.%{name}rc
fi

# Configuration
MAIN_CLASS=$2

BASE_JARS="%{name}"

# Set parameters
set_classpath \$BASE_JARS
set_flags \$BASE_FLAGS
set_options \$BASE_OPTIONS

# Let's start
run "\$@"
EOF
}

jahmm_script %{name} be.ac.ulg.montefiore.run.jahmm.apps.cli.Cli
#jahmm_script %{name}-viz be.ac.ulg.montefiore.run.jahmm.apps.JahmmViz

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
%{__rm} -rf %{buildroot}

%post
%update_maven_depmap
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db || :
fi
%endif

%postun
%update_maven_depmap
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db || :
fi
%endif

%files
%defattr(0644,root,root,0755)
%doc CHANGES COPYING README THANKS
%attr(0755,root,root) %{_bindir}/%{name}
#%attr(0755,root,root) %{_bindir}/%{name}-viz
%{_javadir}/%{name}-%{version}.jar
%{_javadir}/%{name}.jar
%dir %{_datadir}/%{name}
%{_datadir}/maven2/poms/*
%config(noreplace) %{_mavendepmapfragdir}/*
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif

%files manual
%defattr(0644,root,root,0755)
%doc user_guide/jahmm-userguide-0.6.1.pdf
%doc user_guide/html
%doc user_guide/xhtml

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}

%files demo
%defattr(-,root,root,0755)
%{_datadir}/%{name}/*
