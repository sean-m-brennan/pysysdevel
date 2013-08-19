#!/bin/bash
## 
## Copyright 2013.  Los Alamos National Security, LLC.
## This material was produced under U.S. Government contract
## DE-AC52-06NA25396 for Los Alamos National Laboratory (LANL), which is
## operated by Los Alamos National Security, LLC for the U.S. Department
## of Energy. The U.S. Government has rights to use, reproduce, and
## distribute this software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS
## NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
## ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
## modified to produce derivative works, such modified software should be
## clearly marked, so as not to confuse it with the version available
## from LANL.
## 
## Licensed under the Mozilla Public License, Version 2.0 (the
## "License"); you may not use this file except in compliance with the
## License. You may obtain a copy of the License at
## http://www.mozilla.org/MPL/2.0/
## 
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
## implied. See the License for the specific language governing
## permissions and limitations under the License.
## 
## 
## Create a self-contained virtual machine
##
## REQUIRES: wget, python, lighttpd, and
##   createrepo if using CentOS, or debarchiver if using Debian, and
##   virtualbox, or qemu-kvm/libvirt
##
## Also needs:
## Kickstart/Preseed files: centos.cfg and/or debian.cfg
## Optional image: ``project''.bmp


VIRTUALIZER=vbox
TARGET_OS=CENTOS
TARGET_ARCH=
VERBOSE=false
OVERSEE=false
OVA_ONLY=false
VM_WORKING_DIR="${PWD}/VM"


VM_SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VM_TFTP_DIR="${VM_WORKING_DIR}/TFTP"
VM_SERVER_PIDS=()
VM_NAME=""
VM_NET_NAME=""

SERVER_IP=10.0.2.2
SERVER_PORT=7999
SERVER_ADDRESS=http://${SERVER_IP}:${SERVER_PORT}


function create_repository {
    here="${PWD}"
    number=$1
    repo_dir="$2"
    cd "${repo_dir}"
    if [ "${TARGET_OS}" = "CENTOS" ]; then
	createrepo ./ --update
    else
	debarchiver --addoverride --autoscanall
	#FIXME needs config file??
    fi
    cd $here
    port=$(printf 8%03d ${number})
    cat >"${VM_WORKING_DIR}/lighttpd_${number}.conf" <<EOF
server.document-root = "${repo_dir}" 
server.port = ${port}
server.bind = "localhost"
server.use-ipv6 = "disable"
dir-listing.activate = "enable" 
EOF
    lighttpd -D -f ${VM_WORKING_DIR}/lighttpd_${number}.conf &
    server_pid=$!
    echo "Serve repository at ${repo_dir} on port ${port} at pid ${server_pid}" 1>&2
    echo "${server_pid}"  ## return value
}


function pull_repository {
    here="${PWD}"
    number=$1
    repo_dir="${VM_WORKING_DIR}/repository${number}"
    repo_remote="$2"
    echo "Pulling repository from ${repo_remote}" 1>&2
    mkdir -p ${repo_dir}
    if $VERBOSE; then
	rsync -auzv -e ssh --progress ${repo_remote}/* ${repo_dir}/ 1>&2
    else
	rsync -az -e ssh ${repo_remote}/* ${repo_dir}/ >/dev/null 2>&1
    fi
    create_repository $number $repo_dir
}


function tftp_prep {
    here=${VM_SRC_DIR}
    declare -a local_repos=("${1}")
    declare -a remote_repos=("${2}")

    SYSLINUX_VERSION=5.00  ## NOTE: 6.01 doesn't work
    SYSLINUX_WEBSITE=http://www.kernel.org/pub/linux/utils/boot/syslinux
    SYSLINUX_DIR=syslinux-${SYSLINUX_VERSION}

    CENTOS_DISTRO=CentOS
    CENTOS_VERSION=6.4
    CENTOS_ARCH=x86_64
    CENTOS_WEBSITE=http://mirror.centos.org/centos/${CENTOS_VERSION}/os/${CENTOS_ARCH}/images/pxeboot
    CENTOS_IMG=initrd.img

    DEBIAN_DISTRO=debian
    DEBIAN_VERSION=wheezy
    DEBIAN_ARCH=amd64
    DEBIAN_WEBSITE=http://ftp.us.debian.org/debian/dists/${DEBIAN_VERSION}/main/installer-${DEBIAN_ARCH}/current/images/cdrom/
    DEBIAN_IMG=initrd.gz


    TARGET_LABEL=$(echo $TARGET_OS | tr '[A-Z]' '[a-z]')
    eval TARGET_DISTRO=\$${TARGET_OS}_DISTRO
    eval TARGET_ARCH=\$${TARGET_OS}_ARCH
    eval TARGET_WEBSITE=\$${TARGET_OS}_WEBSITE
    eval TARGET_IMG=\$${TARGET_OS}_IMG


    mkdir -p "${VM_WORKING_DIR}"
    cd "${VM_WORKING_DIR}"
    echo "Fetch SysLinux" 1>&2
    if $VERBOSE; then
	wget -N ${SYSLINUX_WEBSITE}/${SYSLINUX_DIR}.tar.bz2
    else
	wget -N ${SYSLINUX_WEBSITE}/${SYSLINUX_DIR}.tar.bz2 2>/dev/null
    fi
    if [ ! -d ${SYSLINUX_DIR} ]; then
	if $VERBOSE; then
	    tar xjf ${SYSLINUX_DIR}.tar.bz2
	else
	    tar xjf ${SYSLINUX_DIR}.tar.bz2 >/dev/null
	fi
    fi

    mkdir -p "${VM_TFTP_DIR}/pxelinux.cfg"
    cp ${SYSLINUX_DIR}/core/pxelinux.0 "${VM_TFTP_DIR}/"
    cp ${SYSLINUX_DIR}/com32/chain/chain.c32 "${VM_TFTP_DIR}/"
    cp ${SYSLINUX_DIR}/com32/menu/menu.c32 "${VM_TFTP_DIR}/"
    cp ${SYSLINUX_DIR}/com32/elflink/ldlinux/ldlinux.c32 "${VM_TFTP_DIR}/"
    cp ${SYSLINUX_DIR}/com32/libutil/libutil_com.c32 "${VM_TFTP_DIR}/"
    cd $here
    cp *.cfg "${VM_TFTP_DIR}/"  ## Kickstart files
    cp *.bmp "${VM_TFTP_DIR}/"
    cp *.png "${VM_TFTP_DIR}/"
    cat >"${VM_TFTP_DIR}/pxelinux.cfg/default" <<EOF
default menu.c32
prompt 0
timeout 100
ontimeout ${TARGET_LABEL}

LABEL centos
        MENU LABEL CentOS
        kernel ${CENTOS_DISTRO}/vmlinuz
        append initrd=${CENTOS_DISTRO}/initrd.img ks=${SERVER_ADDRESS}/centos.cfg

LABEL debian
        MENU LABEL Debian
        kernel ${DEBIAN_DISTRO}/vmlinuz
        append auto=true  auto url=${SERVER_ADDRESS}/debian.cfg  priority=critical DEBIAN_FRONTEND=noninteractive install debconf/priority=medium debian-installer/allow_unauthenticated=true vga=788 initrd=${DEBIAN_DISTRO}/initrd.gz -- quiet

LABEL localboot
        MENU LABEL Boot from disk
        localboot 0
EOF

    echo "Fetch ${TARGET_DISTRO} boot images" 1>&2
    mkdir -p "${VM_TFTP_DIR}/${TARGET_DISTRO}"
    if $VERBOSE; then
	wget -N -P "${VM_TFTP_DIR}/${TARGET_DISTRO}" ${TARGET_WEBSITE}/vmlinuz
	wget -N -P "${VM_TFTP_DIR}/${TARGET_DISTRO}" ${TARGET_WEBSITE}/${TARGET_IMG}
    else
	wget -N -P "${VM_TFTP_DIR}/${TARGET_DISTRO}" ${TARGET_WEBSITE}/vmlinuz 2>/dev/null
	wget -N -P "${VM_TFTP_DIR}/${TARGET_DISTRO}" ${TARGET_WEBSITE}/${TARGET_IMG} 2>/dev/null
    fi

    set +e
    killall lighttpd >/dev/null 2>&1
    set -e
    ## Start server for kickstart files
    cd ${VM_TFTP_DIR}
    python -m SimpleHTTPServer ${SERVER_PORT} >/dev/null &
    server_pid+=$!
    cd $here
    echo "Kickstart server on port ${SERVER_PORT} at pid ${server_pid}" 1>&2
    VM_SERVER_PIDS+=${server_pid}

    idx=0
    for repo in "${local_repos[@]}"; do
	VM_SERVER_PIDS+=$(create_repository $idx ${repo})
	idx=$(($idx+1))
    done

    for repo in "${remote_repos[@]}"; do
	VM_SERVER_PIDS+=$(pull_repository $idx ${repo})
	idx=$(($idx+1))
    done
}

function tftp_cleanup {
    set +e
    for pid in "${VM_SERVER_PIDS[@]}"; do
	if [ "${pid}" != "" ]; then
	    kill ${pid} >/dev/null
	fi
    done
    killall python >/dev/null 2>&1
}



function vbox_init {
    name=$1
    vendor=$2
    version=$3
    disk_size=$4
    license_file=$5

    lower_name=$(echo ${name} | tr [:upper:] [:lower:])
    VM_NET_NAME=${lower_name}
    VM_NAME=${lower_name}_vm_${version}_${TARGET_ARCH}
    LOGO_FILE=${lower_name}.bmp

    VBOX_VM_DIR="${VM_WORKING_DIR}"
    export VBOX_USER_HOME="${VBOX_VM_DIR}"
    export VBOX_IPC_SOCKETID=${VM_NET_NAME}
    echo "VBOX home: $VBOX_USER_HOME" 1>&2
    set +e
    killall VBoxSVC >/dev/null 1>&2
    ## Note this query *must* occur now to get VirtualBox.xml used below
    VBoxManage list extpacks | grep PXE | grep E1000 >/dev/null
    if [ $? -eq 0 ]; then
	echo "Using E1000 NIC" 1>&2
	NIC=82540EM
	NIC_TYPE=e1000  ## Requires VirtualBox Extension Pack
    else
	echo "Using PCNet NIC" 1>&2
	NIC=Am79C970A
	NIC_TYPE=pcnet
    fi
    set -e

    VBOX_DEF="${VBOX_VM_DIR}/VirtualBox.xml"
    if [ ! -e "${VBOX_DEF}" ]; then
	xml_file=$(find ${HOME} -name VirtualBox.xml)
	cp "${xml_file}" "${VBOX_DEF}"
    fi
    mv ${VBOX_DEF} ${VBOX_DEF}.old
    sed "s|^\(.*\)defaultMachineFolder=\"[^\"]*\"\(.*\)$|\1defaultMachineFolder=\"${VBOX_VM_DIR}\"\2|" ${VBOX_DEF}.old >${VBOX_DEF}
    VBOX_DIR=$(dirname "${VBOX_DEF}")
    echo "Using VirtualBox installation at ${VBOX_DIR}" 1>&2

    if [ ! -d "${VBOX_VM_DIR}/${VM_NAME}" ]; then
	here="${PWD}"
	cd "${VBOX_VM_DIR}"
	echo "Create a VirtualBox machine" 1>&2
	VBoxManage createvm --name "${VM_NAME}" --ostype RedHat_64 --register
	VBoxManage createhd --filename "${VM_NAME}/${VM_NAME}.vdi" --size ${disk_size}
	VBoxManage storagectl "${VM_NAME}" --name "SATA Controller" --add sata --controller IntelAHCI --hostiocache on
	VBoxManage storageattach "${VM_NAME}" --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "${VM_NAME}/${VM_NAME}.vdi"
	VBoxManage modifyvm "${VM_NAME}" --memory 2048
	VBoxManage modifyvm "${VM_NAME}" --boot1 disk --boot2 net --boot3 dvd --boot4 none
	if [ -e "${VM_SRC_DIR}/${LOGO_FILE}" ]; then
	    echo "Using logo: ${VM_SRC_DIR}/${LOGO_FILE}"
	    cp "${VM_SRC_DIR}/${LOGO_FILE}" "${VM_NAME}/"
	    VBoxManage modifyvm "${VM_NAME}" --bioslogoimagepath "${LOGO_FILE}"
	fi
	VBoxManage modifyvm "${VM_NAME}" --nictype1 ${NIC}
	VBoxManage modifyvm "${VM_NAME}" --nic1 nat
	VBoxManage setextradata "${VM_NAME}" "VBoxInternal/Devices/${NIC_TYPE}/0/LUN#0/Config/BootFile" "pxelinux.0"
	VBoxManage setextradata "${VM_NAME}" "VBoxInternal/Devices/${NIC_TYPE}/0/LUN#0/Config/TFTPPrefix" "${VM_TFTP_DIR}"
	VBoxManage setextradata "${VM_NAME}" "GUI/Input/AutoCapture" "false"
	VBoxManage setextradata global "GUI/SuppressMessages" "remindAboutAutoCapture,confirmInputCapture,remindAboutMouseIntegrationOn,remindAboutWrongColorDepth,confirmGoingFullscreen,remindAboutMouseIntegrationOff,remindAboutInputCapture"
	cd $here
	if ! $OVA_ONLY; then
	    cat >install_${VM_NAME}.sh <<EOF
#!/bin/sh
VBoxManage registervm "${VM_NAME}/${VM_NAME}.vbox"
EOF
	fi
    else  ## already exists
	VBoxManage registervm "${VM_NAME}/${VM_NAME}.vbox"
    fi

    echo "Install using kickstart over PXE" 1>&2
    if $OVERSEE; then
	VirtualBox --startvm "${VM_NAME}"
    else
	echo "Headless install - no feedback." 1>&2
	VBoxHeadless --startvm "${VM_NAME}"
    fi

    VBoxManage setextradata "${VM_NAME}" "VBoxInternal/Devices/${NIC_TYPE}/0/LUN#0/Config/BootFile"
    VBoxManage setextradata "${VM_NAME}" "VBoxInternal/Devices/${NIC_TYPE}/0/LUN#0/Config/TFTPPrefix"
    if [ -e "${PWD}/${VM_NAME}.ova" ]; then
	rm "${PWD}/${VM_NAME}.ova"
    fi
    if [ -e ${license_file} ]; then
	VBoxManage export "${VM_NAME}" -o "${PWD}/${VM_NAME}.ova" --vsys 0 --product ${name} --vendor ${vendor} --version ${version} --eulafile ${license_file}
    else
	VBoxManage export "${VM_NAME}" -o "${PWD}/${VM_NAME}.ova" --vsys 0 --product ${name} --vendor ${vendor} --version ${version}
    fi
    if [ -e "${VM_SRC_DIR}/${LOGO_FILE}" ]; then
	tar -xf "${VM_NAME}.ova" "${VM_NAME}.ovf"
	mv "${VM_NAME}.ovf" "${VM_NAME}.ovf.old"
	sed "s|^\(.*\)\(<File ovf[^/>]*/>\)\(.*\)$|\1\2\n    <File ovf:href=\"diorama.bmp\" ovf:id=\"file2\"/>\3|" "${VM_NAME}.ovf.old" >"${VM_NAME}.ovf"
	tar -uf "${VM_NAME}.ova" "${VM_NAME}.ovf"
	tar -rf "${VM_NAME}.ova" "${VM_SRC_DIR}/${LOGO_FILE}"
	rm -f *.ovf*
    fi
}

function vbox_cleanup {
    set +e
    echo "Restore original VirtualBox config" 1>&2
    VBoxManage unregistervm "${VM_NAME}"
    unset VBOX_USER_HOME
    unset VBOX_IPC_SOCKETID
}



function kvm_init {
    name=$1
    vendor=$2
    version=$3
    disk_size=$4
    license_file=$5

    lower_name=$(echo ${name} | tr [:upper:] [:lower:])
    VM_NET_NAME=${lower_name}
    VM_NAME=${lower_name}_vm_${version}_${TARGET_ARCH}
    LOGO_FILE=${lower_name}.bmp

    ## To connect to the hypervisor as a non-root user,
    ##  edit /etc/libvirt/libvirtd.conf (if the user is a member of 'libvirt')
    ##    unix_sock_group = "libvirt"
    ##    unix_sock_ro_perms = "0777"
    ##    unix_sock_rw_perms = "0770"
    ##    auth_unix_ro = "none"
    ##    auth_unix_rw = "none"
    virsh connect qemu:///system

    if [ ! -d "${VM_WORKING_DIR}/${VM_NAME}" ]; then
	here="${PWD}"
	cd "${VM_WORKING_DIR}"
	echo "Create KVM machine" 1>&2
	mkdir -p "${VM_NAME}"
	qemu-img create -f qcow2 "${VM_NAME}/${VM_NAME}".img ${disk_size}M
	if [ -e "${VM_SRC_DIR}/${LOGO_FILE}" ]; then
	    echo "Using logo: ${VM_SRC_DIR}/${LOGO_FILE}"
	    cp "${VM_SRC_DIR}/${LOGO_FILE}" "${VM_NAME}/"
	fi
	cat >"${VM_NAME}/${VM_NET_NAME}-net.xml" <<EOF
<network>
  <name>${VM_NET_NAME}</name>
  <forward mode='nat' />
  <ip address="10.0.2.2" netmask="255.255.255.0">
    <tftp root="${VM_TFTP_DIR}"/> 
    <dhcp>
      <range start="10.0.2.3" end="10.0.2.50" />
      <bootp file="pxelinux.0"/>           
    </dhcp>
  </ip>
</network>
EOF
	cat >"${VM_NAME}/${VM_NAME}.xml" <<EOF
<domain type='kvm'>
  <name>${VM_NAME}</name>
  <os>
    <type arch='x86_64' machine='pc'>hvm</type>
    <boot dev='hd'/>
    <boot dev='network'/>
    <boot dev='cdrom'/>
    <bootmenu enable='yes' splash='${LOGO_FILE}'/>
  </os>
  <memory>2048</memory>
  <vcpu>1</vcpu>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='raw' cache='none' io='threads'/>
      <source dev='${VM_NAME}.img'/>
      <target dev='hda' bus='ide'/>
      <address type='drive' controller='0' bus='0' unit='0'/>
    </disk>
    <interface type='network'>     
      <mac address='52:54:00:66:79:14'/>
      <source network='${VM_NET_NAME}'/>      
      <target dev='vnet0'/>
      <alias name='net0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <graphics type='vnc' port='-1' autoport='yes' keymap='en-us'/>
  </devices>
</domain>
EOF
	cat >install_${VM_NAME}.sh <<EOF
#!/bin/sh
virsh create "${VM_NAME}/${VM_NAME}.xml"
EOF
    fi

    virsh net-create --file "${VM_WORKING_DIR}/${VM_NAME}/${VM_NET_NAME}-net.xml"
    virsh create "${VM_WORKING_DIR}/${VM_NAME}/${VM_NAME}.xml"

    virsh start "${VM_NAME}"
    if $OVERSEE; then
	virt-viewer "${VM_NAME}"
    else
	echo "Headless install - no feedback." 1>&2
    fi
}

function kvm_cleanup {
    set +e
    echo "Restore original KVM config" 1>&2
    virsh net-destroy ${VM_NET_NAME}
}



function vm_init {
    declare -a local=("${1}")
    declare -a remote=("${2}")
    tftp_prep "${local[@]}" "${remote[@]}"
    shift
    shift
    if [ "${VIRTUALIZER}" = "kvm" ]; then
	kvm_init $@
    else
	vbox_init $@
    fi
}

function vm_cleanup {
    set +e
    if [ "${VIRTUALIZER}" = "kvm" ]; then
	kvm_cleanup
    else
	vbox_cleanup
    fi
    tftp_cleanup
}



function create_virtual_machine {
    cleanup_only=false
    local_repos=()
    remote_repos=()
    disk_size=8096
    name="project"
    vendor="me"
    license_file="LICENSE"
    version=$(date +%Y%m%d)

    args=""
    while test $# -gt 0; do
	case $1 in
	    --local)
		local_repos=("${2}")
		shift
		;;
	    --remote)
		remote_repos=("${2}")
		shift
		;;
	    --name)
		name=$2
		shift
		;;
	    --vendor)
		vendor=$2
		shift
		;;
	    --license)
		license_file=$2
		shift
		;;
	    --disk)
		disk_size=$2
		shift
		;;
	    --version)
		version=$2
		shift
		;;

	    --kvm)
		VIRTUALIZER=kvm
		;;
	    --vbox | --virtualbox)
		VIRTUALIZER=vbox
		;;
	    --ova)
		OVA_ONLY=true
		;;
	    --debian)
		TARGET_OS=DEBIAN
		;;
	    --centos)
		TARGET_OS=CENTOS
		;;
	    --cleanup)
		cleanup_only=true
		;;
	    -v | --verbose)
		VERBOSE=true
		;;
	    --watch)
		OVERSEE=true
		;;

	    --working-dir)
		VM_WORKING_DIR=$2
		shift
		;;

	    -h | --help)
		echo "USAGE: $(basename $0) " 1>&2
		exit
		;;
	    *)
		args="$args $1"
		;;
	esac
	shift
    done

    set -e
    trap vm_cleanup EXIT

    if $cleanup_only; then
	exit
    fi
    if [ "${VIRTUALIZER}" = "kvm" ]; then
	OVA_ONLY=false
    fi

    vm_init "${local_repos[@]}" "${remote_repos[@]}" ${name} ${vendor} ${version} ${disk_size} ${license_file}
    if ! $OVA_ONLY; then
	echo "Archiving ${VM_NAME}" 1>&2
	tar cjf ${VM_NAME}.tar.bz2 -C ${VM_WORKING_DIR} ${VM_NAME} install_${VM_NAME}.sh
    fi
}

