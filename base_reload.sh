#!/bin/sh
# This script will gracefully restart haproxy without downtime by
# shunting TCP connections directly to a local backend
# Inport  will be shunted to first server
# WARNING: assumes you don't have any other IPTables rules.

#!/bin/sh
# This script will gracefully restart haproxy without downtime by
# shunting TCP connections directly to a local backend
#  port 8000 will be shunted to port 8001
# WARNING: assumes you don't have any other IPTables rules.

# Start remap
remap_start() {{
cat <<EOF | iptables-restore
*nat
:PREROUTING ACCEPT [81699:4934760]
:POSTROUTING ACCEPT [3149436:193315427]
:OUTPUT ACCEPT [3149436:193315427]
{REMAP_START_RULES}
COMMIT
EOF
}}

# continue old remap, but no new ones
remap_pause() {{
cat <<EOF | iptables-restore
*nat
:PREROUTING ACCEPT [81699:4934760]
:POSTROUTING ACCEPT [3149436:193315427]
:OUTPUT ACCEPT [3149436:193315427]
{REMAP_PAUSE_RULES}
COMMIT
EOF
}}

# no more remap
remap_stop() {{
cat <<EOF | iptables-restore
*nat
:PREROUTING ACCEPT [81699:4934760]
:POSTROUTING ACCEPT [3149436:193315427]
:OUTPUT ACCEPT [3149436:193315427]
COMMIT
EOF
}}

# don't return until all remaps are drained
remap_detect() {{
{REMAP_DETECT}
sleep 2
done
}}

# restart ha proxy
restart_ha_proxy() {{
haproxy -f {hap_conf} -p {hap_pid} -st $(cat {hap_pid});
}}

remap_start   # Start forwarding new connections

sleep 1     # Give iptables time to kick in
restart_ha_proxy
sleep 1       # Give new server time to start up and listen

remap_pause   # Stop forwarding new connections, but continue with old
remap_detect  # wait for old connections to drain
remap_stop    # Stop all forwarding

echo "done."