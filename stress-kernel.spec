Name: stress-kernel

%define ctcs_version 1.2.15
%define addon_version 0.9

Version: %{ctcs_version}
Release: 19

Obsoletes: ttcp

Summary: A suite of tools designed to stress the Linux kernel to expose bugs.
Group: Applications/System

License: GPL-2.0

Source0: http://prdownloads.sourceforge.net/va-ctcs/ctcs-%{ctcs_version}.tar.gz
Patch0: ctcs-nox86.patch
Patch10: nox86_asm.patch
Patch11: ltp_on.patch
Patch12: ctcs-heartbeat.patch
Patch13: ctcs-exit.patch
Patch14: ctcs-autoreport.patch
Patch15: ctcs-dummy.patch
Patch16: ctcs-automake-tcf.patch
Patch17: ltp-bogus-getgroup.patch
Patch18: ctcs-notify.patch
Patch19: ctcs-wait.patch

Source1: http://gatekeeper.dec.com/pub/BSD/NetBSD/packages/1.3/mips/All/ttcp.tgz
Patch1: ttcp-proto.patch

Source2: http://www.capecod.net/~rcooper/download/IOtest30.tgz
Patch2: iotest30-offby1.patch
Patch20: iotest30-lseek.patch

Source3: http://www.bit-net.com/~rmiller/ftp/dt/dt-sources.tgz
Patch3: dt-linux-FIFO.patch
Patch30: dt-nodepend.patch
Patch31: dt-64bit.patch

Source4: P3-%{addon_version}.tgz

Source5: fs-%{addon_version}.tgz
Patch50: add_trunc_test.patch
Patch51: trunc_loop.patch
Patch52: ftruncate_cleanup.patch
Patch53: ftruncate64.patch

Source6: drivers-%{addon_version}.tgz
Patch60: crashme_uid.patch
Patch61: crashme_reuseUID.patch
Patch62: ctcs-rawio-rm-null.patch

Source7: misc-%{addon_version}.tgz
Patch70: nfs_findkern.patch
Patch71: hellh-memcalc.patch
Patch72: nfs_sync.patch

Source8: rawio-%{addon_version}.tgz
Patch100: pageh.patch

BuildRoot: /var/tmp/cerberus-broot


%description
A suite of tools to stress the Linux kernel to expose bugs.  The suite is
driven by the Cerberus test protocol.

ExclusiveOS: Linux

# prep section
%prep

%setup -n stress-kernel -c -b 1 -b 2 -b 3 -b 4 -b 5 -b 6 -b 7 -b 8
%patch0 -p0
%patch12 -p0
%patch13 -p0
%patch14 -p0
%patch15 -p0
%patch16 -p0
%patch17 -p0
%patch18 -p0
%patch19 -p0

%ifnarch %{ix86}
%patch10 -p0
%endif

%ifarch %{ix86}
%patch11 -p0
%endif

%patch1 -p0
%patch2 -p0
%patch20 -p0
%patch3 -p0
%patch30 -p0
%patch31 -p0
%patch50 -p0
%patch51 -p0
%patch52 -p0
%patch53 -p0
%patch60 -p0
%patch61 -p0
%patch62 -p0
%patch70 -p0
%patch71 -p0
%patch72 -p0
%patch100 -p0



%ifnarch %{ix86}
perl -pi -e "s/-mpentiumpro//" `find ctcs-%{ctcs_version} -name Makefile` >> /dev/null
perl -pi -e "s/-m486 -malign-loops=2 -malign-functions=2 -malign-jumps=2//" `find ttcp -name Makefile` >> /dev/null
%endif

#
#build
#

%build

NRPROC=`egrep -c "^cpu[0-9]+" /proc/stat || :` 
if [ $NRPROC -eq 0 ] ; then
        NRPROC=1
fi

cd $RPM_BUILD_DIR/stress-kernel/ctcs-%{ctcs_version}
make || :
make

cd $RPM_BUILD_DIR/stress-kernel/ttcp
make

cd $RPM_BUILD_DIR/stress-kernel/iotest30
make -j $NRPROC

cd $RPM_BUILD_DIR/stress-kernel/dt.d
make -j $NRPROC

cd $RPM_BUILD_DIR/stress-kernel/P3
make all

cd $RPM_BUILD_DIR/stress-kernel/fs
make all

cd $RPM_BUILD_DIR/stress-kernel/drivers
#nothing to be done for drivers yet

cd $RPM_BUILD_DIR/stress-kernel/misc
make

cd $RPM_BUILD_DIR/stress-kernel/rawio
make

#
#install
#
%install

rm -rf $RPM_BUILD_ROOT >> /dev/null 2>&1
mkdir -p $RPM_BUILD_ROOT/usr/bin

CTCS_BASE=$RPM_BUILD_ROOT/usr/bin/ctcs
rm -rf $CTCS_BASE

CTCS_RUN_DIR=$CTCS_BASE/runin

cp -ra $RPM_BUILD_DIR/stress-kernel/ctcs-%{ctcs_version} $CTCS_BASE >> /dev/null 2>&1
cp $RPM_BUILD_DIR/stress-kernel/ttcp/ttcp $CTCS_RUN_DIR
cp $RPM_BUILD_DIR/stress-kernel/iotest30/IOtest $CTCS_RUN_DIR
cp $RPM_BUILD_DIR/stress-kernel/dt.d/dt $CTCS_RUN_DIR
cp -ra $RPM_BUILD_DIR/stress-kernel/P3 $CTCS_RUN_DIR
cp -ra $RPM_BUILD_DIR/stress-kernel/fs $CTCS_RUN_DIR
cp -ra $RPM_BUILD_DIR/stress-kernel/rawio $CTCS_RUN_DIR

for I in $RPM_BUILD_DIR/stress-kernel/drivers/* ; do {
    cp $I $CTCS_RUN_DIR
} ; done

for I in $RPM_BUILD_DIR/stress-kernel/misc/{autorun.sh,runreport.sh,make-tcf.sh,hell-hound.sh,README.redhat} ; do {
    cp $I $CTCS_BASE
} ; done

cp $RPM_BUILD_DIR/stress-kernel/misc/save_state.sh $CTCS_RUN_DIR
cp $RPM_BUILD_DIR/stress-kernel/misc/getpagesize $CTCS_RUN_DIR

mkdir -p $RPM_BUILD_ROOT/var/autoreportctcs/{configs,reports}
touch $RPM_BUILD_ROOT/var/autoreportctcs/configs/admins
rm -rf $RPM_BUILD_ROOT/var/autoreportctcs/admins
#
#files
#
%files
%attr(755,root,root) /usr/bin/ctcs
%attr(744,root,root) /var/autoreportctcs
%config(noreplace) /var/autoreportctcs/configs/admins

%preun
CTCS_BASE=${RPM_INSTALL_PREFIX}/usr/bin/ctcs
rm -rf /usr/src/FIFO.tmp.* >> /dev/null 2>&1
rm -rf $CTCS_BASE/RH-test.tcf >> /dev/null 2>&1
rm -rf $CTCS_BASE/.RH-test.tcf.log.* >> /dev/null 2>&1
rm -rf $CTCS_BASE/runin/core >> /dev/null 2>&1

%changelog
* Tue Feb 18 2003 Bill Nottingham <notting@redhat.com>
- fix sigchld fun in ctcs

* Fri Jan 31 2003 Tom Coughlan <coughlan@redhat.com>
- Modify iotest30 so that it tolerates an error from lseek
  when the offset is beyond the end of the device.  This is required
  for kernels 2.4.11 and above.  

* Tue Jan 28 2003 Doug Ledford <dledford@redhat.com>
- Make the nfs loopback mount sync instead of async to see if that
  stops the nfs compile failures.

* Wed Jan 15 2003 Tom Coughlan <coughlan@redhat.com>
- Fix rawio-driver.sh so it no longer deletes /dev/null.

* Wed Jan 16 2002 Bob Matthews <bmatthews@redhat.com>
- Add auto generated TCF files, misc cleanups for automation
- Bump to -15

* Tue Jan 14 2002 Bob Matthews <bmatthews@redhat.com>
- Cleanups for automation, bump to -14

* Tue Jan  8 2002 Bob Matthews <bmatthews@redhat.com>
- First set of automation patches (heartbeat, autorun, autoreport)

* Mon Dec  3 2001 Bob Matthews <bmatthews@redhat.com>
- Add ftruncate64 test to fs suite

* Thu Nov  8 2001 Bob Matthews <bmatthews@redhat.com>
- No screen blanking when executing from config script
- Update README.redhat
- Fix for crashme_driver on IA64

* Thu Oct  2 2001 Bob Matthews <bmatthews@redhat.com>
- Rewrite crashme driver, runs as non-root on both 
-   7.2 and pre-7.2 systems.

* Thu Sep 20 2001 Bob Matthews <bmatthews@redhat.com>
- Crashme again runs as nobody

* Wed Sep 19 2001 Bob Matthews <bmatthews@redhat.com>
- Crashme no longer runs as nobody

* Thu Aug 16 2001 Bob Matthews <bmatthews@redhat.com>
- Add dummy test which saves /proc/ksyms

* Mon Jul 23 2001 Bob Matthews <bmatthews@redhat.com>
- Allow user to reserve additional memory in test config script

* Thu Jul 19 2001 Bob Matthews <bmatthews@redhat.com>
- Fix "cp -pRd" bug in nfstest

* Wed Jul 18 2001 Bob Matthews <bmatthews@redhat.com>
- Transit to ctcs 1.2.15
- Make nfs test smarter and verboser

* Thu Jul  5 2001 Bob Matthews <bmatthews@redhat.com>
- Fix rawio test: was not cleaning up
- Fix floating point test: was not correctly signalling errors

* Fri Jun 29 2001 Bob Matthews <bmatthews.@redhat.com>
- Configuration program should warn when swap < 2*ram, not when swap <= 2*ram

* Thu Jun 21 2001 Bob Matthews <bmatthews@redhat.com>
- Clean up source tags in .spec file
- Make "make sources" work correctly in all cases

* Mon May  7 2001 Bob Matthews <bmatthews@redhat.com>
- Don't lug around data for FP test in rpm; build on the fly instead

* Wed May  2 2001 Bob Matthews <bmatthews@redhat.com>
- Make nfstest build vmlinux, not bzImage
- Fix bugs in nfstest clean, so it won't clobber /usr/src/linux
- fs-test is a slob; won't clean up after itself

* Tue May  1 2001 Bob Matthews <bmatthews@redhat.com>
- Reserve 256MB for kernel on PAE machines
- Reserve 64MB for kernel on non-PAE

* Mon Apr 30 2001 Bob Matthews <bmatthews@redhat.com>
- Cerberus uses RAM + Swap/2 - 32MB for all machines.
- Config script prints warning if SWAP < 2*RAM

* Tue Apr 17 2001 Bob Matthews <bmatthews@redhat.com>
- Tweaked config script memory allocation algorithms
- to better match 2.4 kernels VM behavior.

* Fri Apr 13 2001 Bob Matthews <bmatthews@redhat.com>
- Add Andrea Archangeli's rawio test

* Tue Apr 03 2001 Bob Matthews <bmatthews@redhat.com>
- Add explicit instructions for running NFS tests.

* Sun Apr 01 2001 Michael K. Johnson <johnsonm@redhat.com>
- do not litter BUILD directory, work from stress-kernel directory instead
- obsolete ttcp, don't manually remove it in %pre
- $NRPROC
- fixed relocatability issues
- random cleanups

* Wed Mar 21 2001 Bill Nottingham <notting@redhat.com>
- clean up some x86-isms

* Thu Mar  1 2001 Bob Matthews <bmatthews@redhat.com>
- Made package relocatable
- Fixed dumb bug which caused LTP to leave garbage around
- Exorcist was leaving bunches of zombies on heavily loaded systems

* Fri Feb 23 2001 Bob Matthews <bmatthews@redhat.com>
- added Ingo's directory hammer test ("exorcist") to
- the file system suite

* Fri Feb 16 2001 Bob Matthews <bmatthews@redhat.com>
- misc cleanups in drivers

* Fri Jan 12 2001 Bob Matthews <bmatthews@redhat.com>
- hopefully finally fixed memory requirements specs in hellhound

* Tue Jan  9 2001 Bob Matthews <bmatthews@redhat.com>
- added SGI Linux test project iogen/doio tests to fs-test suite
- changed memory requirements of FS test to accomodate above

* Mon Jan  8 2001 Bob Matthews <bmatthews@redhat.com>
- made crashme run as "nobody" rather than "root"
- fixed wrong documentation about IDE test

* Wed Dec 20 2000 Bob Matthews <bmatthews@redhat.com>
- fixed bug in nfs-test.sh sleep which caused it to sleep 
- forever under certain situations

* Mon Dec 18 2000 Bob Matthews <bmatthews@redhat.com>
- added nfs-test.sh sleep code that waits for all "nfsd"s 
- to exit before restarting nfs services

* Mon Dec 18 2000 Bob Matthews <bmatthews@redhat.com>
- added support for "crashme" to hell-hound driver script
- updated README.redhat

* Mon Dec 11 2000 Bob Matthews <bmatthews@redhat.com>
- moved to ctcs 1.2.14

* Mon Dec 11 2000 Bob Matthews <bmatthews@redhat.com>
- started changlog like I was supposed to months ago :)
