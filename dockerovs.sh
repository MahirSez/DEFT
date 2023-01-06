#!/bin/sh
# Shell script to connect docker container with OpenFlow enabled OVS switches
#
# Inspired from http://ewen.mcneill.gen.nz/blog/entry/2014-10-07-ryu-and-openvswitch-on-docker/
#  and http://ewen.mcneill.gen.nz/blog/media/docker-ovs/dockerovs
# Writen by Aman Mangal  <amanmangal@gatech.edu>, Jan 3, 2015
#----------------------------------------------------------------------------

## Use cases
# ./dockerovs add-br <bridge> <CIDR>
# ./dockerovs del-br <bridge>
# ./dockerovs add-port <guest-id> <bridge> <IP> <gw>
# ./dockerovs cleanup

## give up on errors
set -e

## setup
PATH=/sbin:/usr/bin:/bin
export PATH

## add-br sub-command
add_bridge()
{
  OVS_BRIDGE=$1
  CIDR=$2
  if [ -z "${OVS_BRIDGE}" -o -z "${CIDR}" ]; then
    echo "usage: add-br <bridge> <CIDR>"
    exit 1
  fi

  # delete the existing bridge if any
  if (ifconfig | grep "${OVS_BRIDGE}" > /dev/null) ; then
    ovs-vsctl del-br "${OVS_BRIDGE}"
  fi

  # Ensure the Open vSwitch exists, and will speak OpenFlow 1.0
  ovs-vsctl --may-exist add-br "${OVS_BRIDGE}"
  ovs-vsctl set bridge "${OVS_BRIDGE}" protocols=OpenFlow10
  ip addr add "${CIDR}" dev "${OVS_BRIDGE}"
  ip link set dev "${OVS_BRIDGE}" up

  # Set controller if there is not one already
  EXISTING_CONTROLLER=$(ovs-vsctl get-controller "${OVS_BRIDGE}")
  if [ -z "${EXISTING_CONTROLLER}" ]; then
    ovs-vsctl set-controller "${OVS_BRIDGE}" "tcp:127.0.0.1:6633"
  fi

  echo "new bridge named ${OVS_BRIDGE} with ip ${CIDR} added"
}

## delete bridge
delete_bridge()
{
  OVS_BRIDGE=$1
  if [ -z "${OVS_BRIDGE}" ]; then
    echo "usage: del-br <bridge>"
    exit 1
  fi

  ovs-vsctl --if-exists del-br "${OVS_BRIDGE}"
  echo "successfully deleted ${OVS_BRIDGE}"
}

add_port()
{
  GUEST_NAME=$1
  OVS_BRIDGE=$2
  IP4_ADDR=$3
  IP4_GW=$4

  # NULL Aargument check
  if [ -z "${GUEST_NAME}" -o -z "${OVS_BRIDGE}" -o -z "${IP4_ADDR}" -o -z "${IP4_GW}" ]; then
    echo "usage: add-port <guest-id> <bridge> <IP> <gw>"
    exit 1
  fi

  # check if the bridge exists
  if ! (ifconfig | grep "${OVS_BRIDGE}" > /dev/null) ; then
    echo "Error: bridge ${OVS_BRIDGE} does not exists!"
    exit 1
  fi

  # Find container mount point, so we can determine network namespace
  GUEST_NAME=$(docker inspect ${GUEST_NAME} | grep Id | awk '{ print $2; }' | awk '{ print substr($1, 2, length($1)-3) }')
  CGROUP_MOUNT=$(grep -w devices /proc/mounts | awk '{ print $2; }')
  if [ -z "${CGROUP_MOUNT}" ]; then
    echo "Error: could not auto-locate cgroup mount point" >&2
    exit 1
  fi

  # Find our container path
  CONTAINER=$(find "${CGROUP_MOUNT}" -name "${GUEST_NAME}*")
  if [ -z "${CONTAINER}" ]; then
    echo "Error: no container found matching ${GUEST_NAME}" >&2
    exit 1
  fi

  # check if multiple containers
  NUM_FOUND=$(echo "${CONTAINER}" | wc -l)
  if [ ! "${NUM_FOUND}" -eq 1 ]; then
    echo "Error: multiple containers found matching ${GUEST_NAME}" >&2
    exit 1
  fi

  # Figure out the namespace PID
  NSPID=$(head -n 1 "${CONTAINER}/tasks")
  if [ -z "${NSPID}" ]; then
    echo "Error: no tasks found in container ${GUEST_NAME}" >&2
    exit 1
  fi

  # Prepare helper directory for "ip netns" support
  mkdir -p /var/run/netns
  rm -f "/var/run/netns/${NSPID}"
  ln -s "/proc/${NSPID}/ns/net" "/var/run/netns/${NSPID}"

  # Create link pair to connect between Open vSwitch and container
  TEMP=$(od -An -N1 -i /dev/random | tr -d ' ')
  HOST_IFNAME="vethp${TEMP}-${NSPID}"
  GUEST_IFNAME="vethg${TEMP}-${NSPID}"
  ip link add name "${HOST_IFNAME}" type veth peer name "${GUEST_IFNAME}"
  ip link set "${HOST_IFNAME}" up

  # Inject guest end of link into the container, as eth0
  ip link set "${GUEST_IFNAME}" netns "${NSPID}"
  ip netns exec "${NSPID}" ip link set dev "${GUEST_IFNAME}" name eth0

  # Push the host end of the link into the Open vSwitch
  ovs-vsctl add-port "${OVS_BRIDGE}" "${HOST_IFNAME}"

  # Configure networking inside the container
  ip netns exec "${NSPID}" ip link set eth0 up
  ip netns exec "${NSPID}" ip addr add "${IP4_ADDR}" dev eth0
  ip netns exec "${NSPID}" ip route add default via "${IP4_GW}"

  echo "added port with ip ${IP4_ADDR} and gateway ${IP4_GW} for guest ${GUEST_NAME}"
}

clean_up()
{
  find -L /var/run/netns -type l -delete
  echo "cleaned up"
}

## parse arguments
case $1 in
  add-br) add_bridge $2 $3
    ;;
  del-br) delete_bridge $2
    ;;
  add-port) add_port $2 $3 $4 $5
    ;;
  cleanup) clean_up
    ;;
  *) echo "usage: `basename ${0}` add-br|del-br|add-port|cleanup arguments"
    exit 1
    ;;
esac
