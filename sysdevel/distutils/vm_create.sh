#!/bin/bash
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
VAGRANT=false
TARGET_OS=CENTOS
TARGET_ARCH=
VERBOSE=false
OVERSEE=false
INSTALLER=false
TARGET_PROVIDER=virtualbox
VM_WORKING_DIR="${PWD}/VM"

VM_SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"
VM_TFTP_DIR="${VM_WORKING_DIR}/TFTP"
VM_SERVER_PIDS=()
VM_NAME=""
VM_NET_NAME=""

SERVER_NAME=$(hostname)
SERVER_IP=${SERVER_NAME}
SERVER_PORT=7999
SERVER_ADDRESS=http://${SERVER_IP}:${SERVER_PORT}



function create_repository {
    here="${PWD}"
    number=$1
    repo_dir="$2"
    cd "${repo_dir}"
    if [ "${TARGET_OS}" = "CENTOS" || "${TARGET_OS}" = "FEDORA" ]; then
	createrepo ./ --update 1>&2
    else
	debarchiver --addoverride --autoscanall 1>&2
	#FIXME needs config file??
    fi
    cd $here
    port=$(printf 8%03d ${number})
    cat >"${VM_WORKING_DIR}/lighttpd_${number}.conf" <<EOF
server.document-root = "${repo_dir}" 
server.port = ${port}
#server.bind = "localhost"
server.use-ipv6 = "disable"
dir-listing.activate = "enable" 
EOF
    lighttpd -D -f ${VM_WORKING_DIR}/lighttpd_${number}.conf 1>&2 &
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
    here="${VM_SRC_DIR}"
    local_repos=()
    remote_repos=()
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
	esac
	shift
    done


    SYSLINUX_VERSION=5.00  ## NOTE: 6.01 doesn't work
    SYSLINUX_WEBSITE=http://www.kernel.org/pub/linux/utils/boot/syslinux
    SYSLINUX_DIR=syslinux-${SYSLINUX_VERSION}

    CENTOS_DISTRO=CentOS
    CENTOS_VERSION=6
    CENTOS_ARCH=x86_64
    CENTOS_WEBSITE=http://mirror.centos.org/centos/${CENTOS_VERSION}/os/${CENTOS_ARCH}
    CENTOS_IMG_SITE=${CENTOS_WEBSITE}/images/pxeboot
    CENTOS_IMG=initrd.img

    FEDORA_DISTRO=Fedora
    FEDORA_VERSION=20
    FEDORA_ARCH=x86_64
    FEDORA_WEBSITE=http://dl.fedoraproject.org/pub/fedora/linux/releases/${FEDORA_VERSION}/Fedora/${FEDORA_ARCH}/os
    FEDORA_IMG_SITE=${FEDORA_WEBSITE}/images/pxeboot
    FEDORA_IMG=initrd.img

    DEBIAN_DISTRO=debian
    DEBIAN_VERSION=wheezy
    DEBIAN_ARCH=amd64
    DEBIAN_WEBSITE=http://ftp.us.debian.org/debian/dists/${DEBIAN_VERSION}/main/installer-${DEBIAN_ARCH}/current
    DEBIAN_IMG_SITE=${DEBIAN_WEBSITE}/images/cdrom
    DEBIAN_IMG=initrd.gz


    TARGET_LABEL=$(echo $TARGET_OS | tr '[A-Z]' '[a-z]')
    eval TARGET_DISTRO=\$${TARGET_OS}_DISTRO
    eval TARGET_ARCH=\$${TARGET_OS}_ARCH
    eval TARGET_WEBSITE=\$${TARGET_OS}_WEBSITE
    eval TARGET_IMG_SITE=\$${TARGET_OS}_IMG_SITE
    eval TARGET_IMG=\$${TARGET_OS}_IMG

    mkdir -p "${VM_WORKING_DIR}"
    cd "${VM_WORKING_DIR}"

    if [ "$TARGET_PROVIDER" != "virtualbox" ]; then
	cd "${here}"
	return 0
    fi

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
    cp *.bmp "${VM_TFTP_DIR}/" 2>/dev/null || true
    cp *.png "${VM_TFTP_DIR}/" 2>/dev/null || true
    cp *.repo "${VM_TFTP_DIR}/" 2>/dev/null || true ## Custom repositories
    #HTTP_PROXY_OPTION="proxy=\"${HTTP_PROXY}\""
    cat >"${VM_TFTP_DIR}/pxelinux.cfg/default" <<EOF
default menu.c32
prompt 0
timeout 100
ontimeout ${TARGET_LABEL}

LABEL centos
        MENU LABEL CentOS
        kernel ${CENTOS_DISTRO}/vmlinuz
        append initrd=${CENTOS_DISTRO}/initrd.img ks=${SERVER_ADDRESS}/ks.cfg ksdevice=eth0 ${HTTP_PROXY_OPTION}

LABEL fedora
        MENU LABEL Fedora
        kernel ${FEDORA_DISTRO}/vmlinuz
        append initrd=${FEDORA_DISTRO}/initrd.img ks=${SERVER_ADDRESS}/ks.cfg ksdevice=eth0 ${HTTP_PROXY_OPTION}

LABEL debian
        MENU LABEL Debian
        kernel ${DEBIAN_DISTRO}/vmlinuz
        append auto=true  auto url=${SERVER_ADDRESS}/ks.cfg ${HTTP_PROXY_OPTION} priority=critical DEBIAN_FRONTEND=noninteractive install debconf/priority=medium debian-installer/allow_unauthenticated=true vga=788 initrd=${DEBIAN_DISTRO}/initrd.gz -- quiet

LABEL localboot
        MENU LABEL Boot from disk
        localboot 0
EOF

    echo "Fetch ${TARGET_DISTRO} boot images" 1>&2
    mkdir -p "${VM_TFTP_DIR}/${TARGET_DISTRO}"
    if $VERBOSE; then
	wget -N -P "${VM_TFTP_DIR}/${TARGET_DISTRO}" ${TARGET_IMG_SITE}/vmlinuz
	wget -N -P "${VM_TFTP_DIR}/${TARGET_DISTRO}" ${TARGET_IMG_SITE}/${TARGET_IMG}
    else
	wget -N -P "${VM_TFTP_DIR}/${TARGET_DISTRO}" ${TARGET_IMG_SITE}/vmlinuz 2>/dev/null
	wget -N -P "${VM_TFTP_DIR}/${TARGET_DISTRO}" ${TARGET_IMG_SITE}/${TARGET_IMG} 2>/dev/null
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
    if [ "${#local_repos[@]}" -gt "0" ] && [ "${local_repos[0]}" != "" ]; then
        for repo in "${local_repos[@]}"; do
  	    echo "Local repository  $repo"
	    VM_SERVER_PIDS+=$(create_repository $idx ${repo})
	    idx=$(($idx+1))
        done
    fi

    if [ "${#remote_repos[@]}" -gt "0" ] && [ "${remote_repos[0]}" != "" ]; then
        for repo in "${remote_repos[@]}"; do
	    echo "Remote repository  $repo"
	    VM_SERVER_PIDS+=$(pull_repository $idx ${repo})
	    idx=$(($idx+1))
        done
    fi
}

function tftp_cleanup {
    if [ "$TARGET_PROVIDER" != "virtualbox" ]; then
	return 0
    fi

    set +e
    for pid in "${VM_SERVER_PIDS[@]}"; do
	if [ "${pid}" != "" ]; then
	    kill ${pid} >/dev/null 2>&1
	fi
    done
    killall python >/dev/null 2>&1
    killall lighttpd >/dev/null 2>&1
}



function vbox_init {
    name=$1
    vendor=$2
    version=$3
    mem_size=$4
    disk_size=$5
    license_file=$6
    nataddr=$7
    hostonly=$8
    name_extra=$9

    lower_name=$(echo ${name} | tr [:upper:] [:lower:])
    VM_NET_NAME=${lower_name}
    VM_NAME=${lower_name}_vm_${version}_${TARGET_ARCH}${name_extra}
    LOGO_FILE=${lower_name}.bmp

    VBOX_VM_DIR="${VM_WORKING_DIR}"
    ORIG_HOME="${VBOX_USER_HOME}"
    if [ "x$ORIG_HOME" = "x" ]; then
	ORIG_HOME="${XDG_CONFIG_HOME}"
	if [ "x$ORIG_HOME" = "x" ]; then
	    ORIG_HOME="${HOME}"
	fi
    fi
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
    killall VBoxSVC >/dev/null 1>&2
    set -e

    VBOX_DEF="${VBOX_VM_DIR}/VirtualBox.xml"
    if [ ! -e "${VBOX_DEF}" ]; then
	xml_file=$(find ${ORIG_HOME}/.VirtualBox -name VirtualBox.xml -print -quit)
	if [ $? -ne 0 ]; then
	    echo "VirtualBox must be run at least once before using this script."
	    exit 1
	fi
	cp "${xml_file}" "${VBOX_DEF}"
    fi
    mv ${VBOX_DEF} ${VBOX_DEF}.old
    sed "s|^\(.*\)defaultMachineFolder=\"[^\"]*\"\(.*\)$|\1defaultMachineFolder=\"${VBOX_VM_DIR}\"\2|" ${VBOX_DEF}.old >${VBOX_DEF}
    VBOX_DIR=$(dirname "${VBOX_DEF}")
    echo "Using VirtualBox from ${VBOX_DIR}" 1>&2
    cat ${VBOX_DEF} | grep defaultMachineFolder 1>&2

    if [ ! -d "${VBOX_VM_DIR}/${VM_NAME}" ]; then
	here="${PWD}"
	cd "${VBOX_VM_DIR}"
	echo "Create a VirtualBox machine" 1>&2
	VBoxManage createvm --name "${VM_NAME}" --ostype RedHat_64 --register
	VBoxManage createhd --filename "${VM_NAME}/${VM_NAME}.vdi" --size ${disk_size}
	VBoxManage storagectl "${VM_NAME}" --name "SATA Controller" --add sata --controller IntelAHCI --hostiocache on
	VBoxManage storageattach "${VM_NAME}" --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "${VM_NAME}/${VM_NAME}.vdi"
	VBoxManage modifyvm "${VM_NAME}" --memory ${mem_size}
	VBoxManage modifyvm "${VM_NAME}" --boot1 disk --boot2 net --boot3 dvd --boot4 none
	if [ -e "${VM_SRC_DIR}/${LOGO_FILE}" ]; then
	    echo "Using logo: ${VM_SRC_DIR}/${LOGO_FILE}"
	    cp "${VM_SRC_DIR}/${LOGO_FILE}" "${VM_NAME}/"
	    VBoxManage modifyvm "${VM_NAME}" --bioslogoimagepath "${VM_NAME}/${LOGO_FILE}"
	fi

	if [ "$nataddr" = "0" ]; then
	    nataddr=""
	fi
	VBoxManage modifyvm "${VM_NAME}" --nictype1 ${NIC}
	VBoxManage modifyvm "${VM_NAME}" --nic1 nat
	## Allow static IPs on the NAT network
	VBoxManage modifyvm "${VM_NAME}" --natdnsproxy1 on
	VBoxManage modifyvm "${VM_NAME}" --natdnshostresolver1 on
	echo "Port forwarding to $nataddr"
	VBoxManage modifyvm "${VM_NAME}" --natpf1 "guestweb,tcp,,8080,$nataddr,80"
	VBoxManage modifyvm "${VM_NAME}" --natpf1 "guestssh,tcp,,2222,$nataddr,22"

	VBoxManage setextradata "${VM_NAME}" "VBoxInternal/Devices/${NIC_TYPE}/0/LUN#0/Config/BootFile" "pxelinux.0"
	VBoxManage setextradata "${VM_NAME}" "VBoxInternal/Devices/${NIC_TYPE}/0/LUN#0/Config/TFTPPrefix" "${VM_TFTP_DIR}"

	if [ x"$hostonly" != x0 ]; then
	    echo "Host-Only interface IP ${hostonly}"
	    VBoxManage hostonlyif ipconfig vboxnet0 --ip ${hostonly} --netmask 255.255.255.0
	    if [ $? -ne 0 ]; then
		VBoxManage hostonlyif create
		VBoxManage hostonlyif ipconfig vboxnet0 --ip ${hostonly} --netmask 255.255.255.0
	    fi
	    VBoxManage modifyvm "${VM_NAME}" --nictype2 ${NIC}
	    VBoxManage modifyvm "${VM_NAME}" --nic2 hostonly
	    VBoxManage modifyvm "${VM_NAME}" --hostonlyadapter2 vboxnet0
	fi

	VBoxManage setextradata "${VM_NAME}" "GUI/Input/AutoCapture" "false"
	VBoxManage setextradata global "GUI/SuppressMessages" "remindAboutAutoCapture,confirmInputCapture,remindAboutMouseIntegrationOn,remindAboutWrongColorDepth,confirmGoingFullscreen,remindAboutMouseIntegrationOff,remindAboutInputCapture"
	cd $here
	if $INSTALLER; then
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
    echo "$PWD  $VM_NAME/$LOGO_FILE"
    if [ -e ${VM_NAME}/${LOGO_FILE} ]; then
	echo "Inserting boot logo: ${LOGO_FILE}"
	mkdir ova_tmp
	cp ${VM_NAME}/${LOGO_FILE} ova_tmp/
	tar -xf ${VM_NAME}.ova -C ova_tmp
	mv ova_tmp/${VM_NAME}.ovf ${VM_NAME}.ovf.old
	sed "s|^\(.*\)\(<File ovf[^/>]*/>\)\(.*\)$|\1\2\n    <File ovf:href=\"diorama.bmp\" ovf:id=\"file2\"/>\3|" ${VM_NAME}.ovf.old >ova_tmp/${VM_NAME}.ovf
	tar -cf ${VM_NAME}.ova -C ova_tmp *
	rm -rf ova_tmp
    fi
}

function vbox_cleanup {
    set +e
    echo "Restore original VirtualBox config" 1>&2
    VBoxManage unregistervm "${VM_NAME}"
    unset VBOX_USER_HOME
    unset VBOX_IPC_SOCKETID
    rm -rf /tmp/vbox* || true
    rm -rf /tmp/.vbox* || true
}


function libvirt_init {
    name=$1
    vendor=$2
    version=$3
    mem_size=$4
    disk_size=$5
    license_file=$6
    nataddr=$7
    hostonly=$8
    name_extra=$9

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

    if [[ $(virsh -c qemu:///system list) == *${VM_NAME}* ]]; then
	virsh -c qemu:///system destroy ${VM_NAME}
    fi
    if [[ $(virsh -c qemu:///system list --all) == *${VM_NAME}* ]]; then
	virsh -c qemu:///system undefine ${VM_NAME}
    fi
    if [ ! -d "${VM_WORKING_DIR}/${VM_NAME}" ]; then
	here="${PWD}"
	cd "${VM_WORKING_DIR}"
	echo "Create LibVirt machine" 1>&2
	mkdir -p "${VM_NAME}"
	qemu-img create -f qcow2 "${VM_NAME}/${VM_NAME}".img ${disk_size}M
	## FIXME enable port forwarding?
	#cat >${VM_NAME}/${VM_NET_NAME}-net.xml <<EOF
#EOF
	if [ -e "${VM_SRC_DIR}/${LOGO_FILE}" ]; then
	    echo "Using logo: ${VM_SRC_DIR}/${LOGO_FILE}"
	    cp "${VM_SRC_DIR}/${LOGO_FILE}" "${VM_NAME}/"
	fi
    fi

    if [ -e "${VM_WORKING_DIR}/${VM_NAME}/${VM_NET_NAME}-net.xml" ]; then
	if [[ $(virsh -c qemu:///system net-list --all) != *${VM_NET_NAME}* ]]; then
	    virsh -c qemu:///system net-define --file "${VM_WORKING_DIR}/${VM_NAME}/${VM_NET_NAME}-net.xml"
	    virsh -c qemu:///system net-autostart ${VM_NET_NAME}
	fi
	if [[ $(virsh -c qemu:///system net-list) != *${VM_NET_NAME}* ]]; then
	    virsh -c qemu:///system net-start ${VM_NET_NAME}
	fi
    fi

    virt_type=""
    if [ "$VIRTUALIZER" = "kvm" ]; then
	virt_type="--virt-type=kvm"
    fi

    if $INSTALLER; then
	cat >install_${VM_NAME}.sh <<EOF
#!/bin/sh
virsh -c qemu:///system create "${VM_NAME}/${VM_NAME}.xml"
EOF
    fi

    virt-install --connect qemu:///system --name ${VM_NAME} --ram ${mem_size} \
	--vcpus 1 --noreboot --hvm ${virt_type} --noautoconsole \
	--disk path=${VM_WORKING_DIR}/${VM_NAME}/${VM_NAME}.img,format=qcow2 \
	--network network:default --location=${TARGET_WEBSITE} \
	--initrd-inject=${here}/ks.cfg --extra-args="ks=file:/ks.cfg"

    if $OVERSEE; then
	virt-viewer -c qemu:///system "${VM_NAME}" || true
    else
	echo "Headless install - no feedback." 1>&2
    fi

    while [[ $(virsh -c qemu:///system list) == *${VM_NAME}* ]]; do
	sleep 10
    done

    virsh -c qemu:///system dumpxml ${VM_NAME} >${VM_WORKING_DIR}/${VM_NAME}/${VM_NAME}.xml
}

function libvirt_cleanup {
    set +e
    echo "Restore original LibVirt config" 1>&2
    if [[ $(virsh -c qemu:///system list) == *${VM_NAME}* ]]; then
	virsh -c qemu:///system destroy ${VM_NAME}
    fi
    if [[ $(virsh -c qemu:///system list --all) == *${VM_NAME}* ]]; then
	virsh -c qemu:///system undefine ${VM_NAME}
    fi
    if [[ $(virsh -c qemu:///system net-list) == *${VM_NET_NAME}* ]]; then
	virsh -c qemu:///system net-destroy ${VM_NET_NAME}
    fi
    if [[ $(virsh -c qemu:///system net-list --all) == *${VM_NET_NAME}* ]]; then
	virsh -c qemu:///system net-undefine ${VM_NET_NAME}
    fi
}

function libvirt_port_forwarding {
    name=$1
    vendor=$2
    version=$3
    mem_size=$4
    disk_size=$5
    license_file=$6
    nataddr=$7
    hostonly=$8
    name_extra=$9

    lower_name=$(echo ${name} | tr [:upper:] [:lower:])
    VM_NET_NAME=${lower_name}
    VM_NAME=${lower_name}_vm_${version}_${TARGET_ARCH}

    prologue="#!/bin/bash"
    if [ -e /etc/libvirt/hooks/qemu ]; then
	cp /etc/libvirt/hooks/qemu old_hooks.sh
	prologue=""
    fi
    cat >>/etc/libvirt/hooks/qemu <<EOF
${prologue}

Guest_name="${VM_NAME}"
Host_port=8888
Guest_ipaddr=${nataddr}
Guest_port=80

if [ $1 = $Guest_name ]; then
    if [[ $2 = "stopped" || $2 = "reconnect" ]]; then
        iptables -t nat -D PREROUTING -p tcp --dport $Host_port -j DNAT  --to $Guest_ipaddr:$Guest_port
       	iptables -D FORWARD -d $Guest_ipaddr/32 -p tcp -m state --state NEW,RELATED,ESTABLISHED -m tcp --dport $Guest_port -j ACCEPT
    fi
    if [[ $2 = "start" || $2 = "reconnect" ]]; then
        iptables -t nat -I PREROUTING -p tcp --dport $Host_port -j DNAT --to $Guest_ipaddr:$Guest_port
       	iptables -I FORWARD -d $Guest_ipaddr/32 -p tcp -m state --state NEW,RELATED,ESTABLISHED -m tcp --dport $Guest_port -j ACCEPT
    fi
fi
EOF
    chmod +x /etc/libvirt/hooks/qemu
}



function vagrant_init {
    name=$1
    vendor=$2
    version=$3
    mem_size=$4
    disk_size=$5
    license_file=$6
    nataddr=$7
    lower_name=$(echo ${name} | tr [:upper:] [:lower:])

    export VAGRANT_DEFAULT_PROVIDER=$TARGET_PROVIDER
    if [ "$TARGET_PROVIDER" = "virtualbox" ]; then
	vbox_init $@

	rm -f ${lower_name}.virtual.box
	vagrant package --base ${VM_NAME} --output ${lower_name}.virtualbox.box
    
	vbox_cleanup

    elif [ "$TARGET_PROVIDER" = "libvirt" ] || [ "$TARGET_PROVIDER" = "kvm" ]; then
	libvirt_init $@

	cat >${VM_WORKING_DIR}/${VM_NAME}/metadata.json <<EOF
{
  "provider" : "libvirt",
  "format" : "qcow2",
  "virtual_size" : $(($disk_size / 1024))
}
EOF
	net_name="vagrant"
	if [ "$TARGET_PROVIDER" = "libvirt" ]; then
	    net_name="vagrant-libvirt"
	fi
	virt_type="$VIRTUALIZER"
	if [ "$VIRTUALIZER" = "kvm" ]; then
	    virt_type="qemu"
	fi
	cat >${VM_WORKING_DIR}/${VM_NAME}/Vagrantfile <<EOF
Vagrant.configure("2") do |config|
  config.vm.base_mac = "080027129698"

  # No extra options for kvm vagrant provider (plugin).

  # Options for libvirt vagrant provider (plugin).
  config.vm.provider :libvirt do |libvirt|
    libvirt.driver = "${virt_type}"

    # The name of the server, where libvirtd is running.
    libvirt.host = "localhost"
    # If use ssh tunnel to connect to Libvirt.
    libvirt.connect_via_ssh = false
    # Libvirt storage pool name, where box image and instance snapshots will
    # be stored.
    libvirt.storage_pool_name = "default"

    # The username and password to access Libvirt. Password is not used when
    # connecting via ssh.
    #libvirt.username = "root"
    #libvirt.password = "secret"
  end
end
EOF
	echo "Packaging ${VM_NAME}"
	rm -f ${lower_name}.${TARGET_PROVIDER}.box
	mv "${VM_WORKING_DIR}/${VM_NAME}/${VM_NAME}.img" "${VM_WORKING_DIR}/${VM_NAME}/box.img"

	sed "s|source file='${VM_WORKING_DIR}/${VM_NAME}/${VM_NAME}.img'|source file='box.img'|" <"${VM_WORKING_DIR}/${VM_NAME}/${VM_NAME}.xml" | sed "s|source network='default'|source network='${net_name}'|" >"${VM_WORKING_DIR}/${VM_NAME}/box.xml"
	cd ${here}
	tar czf ${lower_name}.${TARGET_PROVIDER}.box -C "${VM_WORKING_DIR}/${VM_NAME}" metadata.json Vagrantfile box.img ${key_file}

	libvirt_cleanup
    fi
}

function vagrant_cleanup {
    return 0
}


function get_vagrant_location {
    version=$(vagrant --version | cut -d ' ' -f2)
    case $(uname) in
	Linux)
	    prefix="/opt/vagrant"
	    if [ ! -d $prefix ]; then
		## Installed through Ruby
		prefix="/usr/local/vagrant"
	    fi
	    ;;
	Darwin)
	    prefix="/Applications/Vagrant"
	    ;;
	MINGW* | CYGWIN*)
	    prefix=$(which vagrant | xargs dirname | xargs dirname)
	    ;;
    esac
    echo "${prefix}/embedded/gems/gems/vagrant-${version}"
}

function get_vagrant_keys {
    if [ "$1" = "--insecure" ]; then
	echo $(get_vagrant_location)/keys/vagrant.pub
    else
	if [ ! -e vagrant_key ] || [ ! -e vagrant_key.pub ]; then
	    rm -f vagrant_key*
	    ssh-keygen -t rsa -C "Secure vagrant key" -N '' -f vagrant_key -q
	fi
	echo vagrant_key.pub
    fi
}



function vm_init {
    args=""
    prep_args=""
    while test $# -gt 0; do
	case $1 in
	    --local)
		prep_args="$prep_args $1 ${2}"
		shift
		;;
	    --remote)
		prep_args="$prep_args $1 ${2}"
		shift
		;;
	    *)
		args="$args $1"
		;;
	esac
	shift
    done

    tftp_prep $prep_args
    if [ $VAGRANT ]; then
	vagrant_init $args
    else
	if [ "${VIRTUALIZER}" = "vbox" ]; then
	    vbox_init $args
	else
	    libvirt_init $args
	fi
    fi
}

function vm_cleanup {
    set +e
    if [ $VAGRANT ]; then
	vagrant_cleanup
    else
	if [ "${VIRTUALIZER}" = "vbox" ]; then
	    vbox_cleanup
	else
	    libvirt_cleanup
	fi
    fi
    tftp_cleanup
}



function get_target_gateway {
    gw=10.0.2.2  ## virtualbox default
    while test $# -gt 0; do
	case $1 in
	    --kvm | --libvirt)
		gw=$(virsh net-dumpxml default | grep "ip address" | cut -d"'" -f2)
		;;
	esac
	shift
    done
    echo $gw
}

function get_target_subnet {
    ipaddr=$(get_target_gateway $@)
    IFS=. read -r ip1 ip2 ip3 ip4 <<< "$ipaddr"
    printf "%d.%d.%d" "$ip1" "$ip2" "$ip3"
}

function get_target_nameserver {
    ns=10.0.2.3  ## virtualbox default
    while test $# -gt 0; do
	case $1 in
	    --kvm | --libvirt)
		ns=$(get_target_gateway $@)
		;;
	esac
	shift
    done
    echo $ns
}


function create_virtual_machine {
    cleanup_only=false
    local_args=""
    remote_args=""
    mem_size=2048
    disk_size=8096
    name="project"
    vendor="me"
    extra_name=""
    nat_addr="0"
    hostonly_net="0"
    license_file="LICENSE"
    version=$(date +%Y%m%d)

    args=""
    while test $# -gt 0; do
	case $1 in
	    --local)
		local_args="$1 ${2}"
		shift
		;;
	    --remote)
		remote_args="$1 ${2}"
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
	    --memory)
		mem_size=$2
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
	    --extra-name)
		extra_name=$2
		shift
		;;
	    --nat-address)
		nat_addr="$2"
		shift
		;;
	    --hostonly-address)
		hostonly_net="$2"
		shift
		;;
	    --with-installer)
		INSTALLER=true
		;;

	    --kvm)
		VIRTUALIZER=kvm
		if [ $TARGET_PROVIDER = virtualbox ]; then
		    TARGET_PROVIDER=kvm
		fi
		;;
	    --xen)  ## Xen hypervisor
		VIRTUALIZER=kvm
		TARGET_PROVIDER=libvirt
		;;
	    --lxc)  ## Linux Containers
		VIRTUALIZER=kvm
		TARGET_PROVIDER=libvirt
		;;
	    --esx)  ## VMware ESX
		VIRTUALIZER=esx
		TARGET_PROVIDER=libvirt
		;;
	    --vmwarews)  ## VMware Workstation
		VIRTUALIZER=esx
		TARGET_PROVIDER=libvirt
		;;
	    --libvirt)
		if [ $VIRTUALIZER = vbox ]; then
		    VIRTUALIZER=kvm
		fi
		TARGET_PROVIDER=libvirt
		;;
	    --vbox | --virtualbox)
		VIRTUALIZER=vbox
		TARGET_PROVIDER=virtualbox
		;;
	    --vagrant)
		VAGRANT=true
		;;
	    --debian)
		TARGET_OS=DEBIAN
		;;
	    --centos)
		TARGET_OS=CENTOS
		;;
	    --fedora)
		TARGET_OS=FEDORA
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

    vm_init ${name} ${vendor} ${version} ${mem_size} ${disk_size} ${license_file} ${nat_addr} ${hostonly_net} ${extra_name} ${local_args} ${remote_args}
    if $INSTALLER; then
	echo "Archiving ${VM_NAME}" 1>&2
	tar cjf ${VM_NAME}.tar.bz2 -C ${VM_WORKING_DIR} ${VM_NAME} install_${VM_NAME}.sh
    fi
}

