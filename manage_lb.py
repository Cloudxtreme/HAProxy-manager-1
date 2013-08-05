"""
    LB manager
    This Script require HAProxy
"""
from prettytable import PrettyTable
import os


servers = {
    "s1": {
        'address': '127.0.0.1:8001',
    },
    "s2": {
        'address': '127.0.0.1:8002',
    },
}

BASE_CONF = 'base_haproxy.conf'
REAL_CONF = 'haproxy_temp.cfg'
REAL_PID = 'hap.pid'
BASE_SH = 'base_reload.sh'
REAL_SH = 'reload_ha_temp.sh'

MAX_CON_PER_SERV = 32


class Manager(object):
    """
    """
    next_lb_port = 9000
    available_lbs = {}

    def list_lb(self, lb_key=None):
        """
            - returns list of available LBs
        """
        table = PrettyTable(["Name", "Port", "Servers"])
        for key, val in self.available_lbs.iteritems():
            table.add_row([
                '=' * 5 + key + '=' * 5 if key == lb_key else key,
                val["port"], val["servers"],
                ])

        print table

    def create_lb(self, key):
        """
            - Create new non_active LB.
            - No HAProxy restart.
        """
        if key in self.available_lbs:
            raise Exception('Already Exists')

        new_lb = {
            "port": self.next_lb_port,
            "servers": {},
        }
        self.available_lbs[key] = new_lb
        self.next_lb_port += 1
        return self.list_lb(lb_key=key)

    def drop_lb(self, key):
        """
            - Check if LB is active.
            - Drop Lb from list.
            - Reload HAProxy if necessary.
        """
        if not key in self.available_lbs:
            raise Exception('There is no such LB in list')

        old_lb = self.available_lbs.pop(key)

        if len(old_lb['servers']):
            self.reload_hap_proxy()

    def _check_params(self, lb_key, server_key):
        """

        """
        if not lb_key in self.available_lbs:
            raise Exception('There is no such LB in list')

        if not server_key in servers:
            raise Exception('There is no such server in list')

    def add_server_to_lb(self, lb_key, server_key, apply=True):
        """
            - Check if LB with this key Available
            - Add server to Selected LB
            - Reload HAProxy
        """
        self._check_params(lb_key, server_key)

        lb_servers = self.available_lbs[lb_key]['servers']
        if server_key in lb_servers:
            raise Exception('This LB already using this server')

        lb_servers[server_key] = servers[server_key]

        self.list_lb(lb_key=lb_key)

        if apply:
            self.reload_hap_proxy()

    def remove_server_from_lb(self, lb_key, server_key, apply=True):
        """
            - Check if LB with this key Available
            - Add server to Selected LB
            - Reload HAProxy
        """

        self._check_params(lb_key, server_key)

        lb_servers = self.available_lbs[lb_key]['servers']
        if server_key not in lb_servers:
            raise Exception('This Server not used by this LB')

        lb_servers.pop(server_key)
        if apply:
            self.reload_hap_proxy()

    def _generate_config(self):
        """
            Generate config file for HAProxy
        """
        base_conf = open(BASE_CONF, 'r')
        real_conf = open(REAL_CONF, 'w+b')
        real_conf.write(base_conf.read())
        base_conf.close()

        base_server_conf = """
        \n\nlisten {}-in\n\tbind *:{}"""
        backed_entry = "\tserver {} {} maxconn {}"

        for lb_name, lb_data in self.available_lbs.iteritems():
            lb_conf = base_server_conf.format(lb_name, lb_data['port'])
            serv_confs = [backed_entry.format(s_name, s_data['address'], MAX_CON_PER_SERV)
                          for s_name, s_data in lb_data['servers'].iteritems()]
            lb_conf += '\n' + '\n'.join(serv_confs)
            real_conf.write(lb_conf)

        # write 10 times by few lines OR collect all lines and write once ????
        real_conf.close()

    def _generate_script(self):
        """
            Generate reload script
        """
        # ('lb_in_port', 'serv_full_addr', 'serv_ip', 'serv_port')
        # (8000, '127.0.0.1:8001', '127.0.0.1', '8001')
        remap_start = "-A OUTPUT -p tcp -m tcp --dport {0} -m state --state ESTABLISHED -j DNAT --to-destination {1}\n" + \
                    "-A OUTPUT -p tcp -m tcp --dport {0} -m state --state NEW -j DNAT --to-destination {1}"
        remap_pause = "-A OUTPUT -p tcp -m tcp --dport {0} -m state --state ESTABLISHED -j DNAT --to-destination {1}"
        remap_detect = """while egrep "^tcp +[0-9]+ +[0-9]+ +ESTABLISHED src={2} dst=127.0.0.1 sport=[0-9]+ dport={0}.*dst=127.0.0.1 sport={3}" /proc/net/nf_conntrack; do"""

        cont_data = [
            [s_data['port'], s_data['servers'].values()[0]['address']
            ] + s_data['servers'].values()[0]['address'].split(':')
            for s_data in self.available_lbs.values() if s_data["servers"]]

        context = {
            'REMAP_START_RULES': '\n'.join([remap_start.format(*cont) for cont in cont_data]),
            'REMAP_PAUSE_RULES': '\n'.join([remap_pause.format(*cont) for cont in cont_data]),
            'REMAP_DETECT': '\n'.join([remap_detect.format(*cont) for cont in cont_data]),
            'hap_conf': REAL_CONF,
            'hap_pid': REAL_PID,
        }
        sh_template_file = open(BASE_SH, 'r')
        sh_template = sh_template_file.read()
        sh_template_file.close()
        real_sh = open(REAL_SH, 'w+b')
        real_sh.write(sh_template.format(**context))
        real_sh.close()

    def reload_hap_proxy(self):
        """
            - Generate sh script that would reload HAProxy without gracefully
            - Run generated script
        """
        # GENERATE HA_PROXY CONFIG
        self._generate_config()
        # GENERATE RELOAD SCRIPT
        self._generate_script()
        # EXECUTE SCRIPT
        os.system('sudo sh {}'.format(REAL_SH))


def self_test():
    manager = Manager()

    manager.create_lb('ololo')

    manager.add_server_to_lb('ololo', 's1', apply=False)
    manager.add_server_to_lb('ololo', 's2', apply=False)

    manager.reload_hap_proxy()

self_test()