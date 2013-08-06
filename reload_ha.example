#!/bin/sh
# This script will gracefully restart haproxy without downtime by
# shunting TCP connections directly to a local backend
# Inport  will be shunted to first server
# WARNING: assumes you don't have any other IPTables rules.

# Start remap
remap_start() {
cat <<EOF | iptables-restore
*nat
:PREROUTING ACCEPT [81699:4934760]
:POSTROUTING ACCEPT [3149436:193315427]
:OUTPUT ACCEPT [3149436:193315427]
-A OUTPUT -p tcp -m tcp --dport 8000 -m state --state ESTABLISHED -j DNAT --to-destination 127.0.0.1:8001
-A OUTPUT -p tcp -m tcp --dport 8000 -m state --state NEW -j DNAT --to-destination 127.0.0.1:8001
COMMIT
EOF
}

# continue old remap, but no new ones
remap_pause() {
cat <<EOF | iptables-restore
*nat
:PREROUTING ACCEPT [81699:4934760]
:POSTROUTING ACCEPT [3149436:193315427]
:OUTPUT ACCEPT [3149436:193315427]
-A OUTPUT -p tcp -m tcp --dport 8000 -m state --state ESTABLISHED -j DNAT --to-destination 127.0.0.1:8001
COMMIT
EOF
}

# no more remap
remap_stop() {
cat <<EOF | iptables-restore
*nat
:PREROUTING ACCEPT [81699:4934760]
:POSTROUTING ACCEPT [3149436:193315427]
:OUTPUT ACCEPT [3149436:193315427]
COMMIT
EOF
}

# don't return until all remaps are drained
remap_detect() {
while egrep "^tcp +[0-9]+ +[0-9]+ +ESTABLISHED src=127.0.0.1 dst=127.0.0.1 sport=[0-9]+ dport=8000.*dst=127.0.0.1 sport=8001" /proc/net/nf_conntrack; do
echo "waiting for iptables connections to drain on port 8000"
sleep 2
done
}

# restart ha proxy
restart_ha_proxy() {
haproxy -f haproxy.cfg -p hap.pid -st $(cat hap.pid);
#done
}

#service haproxy check    # bail on error

remap_start   # Start forwarding new connections

sleep 1     # Give iptables time to kick in
restart_ha_proxy
sleep 1       # Give new server time to start up and listen

remap_pause   # Stop forwarding new connections, but continue with old
remap_detect  # wait for old connections to drain
remap_stop    # Stop all forwarding

echo "done."