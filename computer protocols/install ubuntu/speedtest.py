import subprocess
import re
import time

hosts = 'zpl-scope', 'zpl-purple', 'zpl-9000', 'zpl-imac', 'dtn01.chpc.wustl.edu'
users = 'zplab', 'zplab', 'zplab', 'pincuslab', 'zpincus'
paths = '', '', '', '/usr/local/bin/', './'

def start_servers():
    servers = []
    for host, user, path in zip(hosts, users, paths):
        servers.append(subprocess.Popen(['ssh', '-tt', f'{user}@{host}', f'{path}iperf3 -s -V -p 5001'], stdin=subprocess.DEVNULL))
    return servers

def stop_servers(servers):
    for server in servers:
        server.terminate()

def estop():
    for host, user in zip(hosts, users):
        subprocess.run(['ssh', f'{user}@{host}', f'killall iperf3'], stdin=subprocess.DEVNULL)

def speedtest():
    output = []
    for fromh, fromu, fromp in zip(hosts, users, paths):
        for toh, tou, top in zip(hosts, users, paths):
            if fromh == toh:
                continue

            out = subprocess.run(['ssh', f'{fromu}@{fromh}', f'{fromp}iperf3 -c {toh} -V -p 5001'], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE)
            m = re.search(r'(\d+\.\d+) Gbits/sec\s+(\d*)\s+sender', out.stdout.decode())
            if not m:
                print('ERROR:')
                print(out.stdout.decode())
                print('------')
            if m is not None:
                gbps, retr = m.groups()
            else:
                gbps = retr = '-'

            rout = subprocess.run(['ssh', f'{tou}@{toh}', f'{top}iperf3 -c {fromh} -R -V -p 5001'], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE)
            rm = re.search(r'(\d+\.\d+) Gbits/sec\s+(\d*)\s+sender', rout.stdout.decode())
            if not rm:
                print('ERROR:')
                print(rout.stdout.decode())
                print('------')
            if rm is not None:
                rgbps, rretr = rm.groups()
            else:
                rgbps = rretr = '-'

            output.append(f'{fromh} -> {toh}: {gbps} / {rgbps} (retr: {retr} / {rretr})')
    print('\n'.join(output))
    return output


def speedtest_to_fixed(server):
    for fromh, fromu, fromp in zip(hosts, users, paths):
        out = subprocess.run(['ssh', f'{fromu}@{fromh}', f'{fromp}iperf3 -c {server} -V'], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE)
        m = re.search(r'(\d+\.\d+) Gbits/sec\s+(\d*)\s+sender', out.stdout.decode())
        if not m:
            print('ERROR:')
            print(out.stdout.decode())
            print('------')
        if m is not None:
            gbps, retr = m.groups()
        else:
            gbps = retr = '-'
        print(f'{fromh} OUT: {gbps} (retr: {retr})')

        rout = subprocess.run(['ssh', f'{fromu}@{fromh}', f'{fromp}iperf3 -c {server} -V -R'], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE)
        rm = re.search(r'(\d+\.\d+) Gbits/sec\s+(\d*)\s+sender', rout.stdout.decode())
        if not rm:
            print('ERROR:')
            print(rout.stdout.decode())
            print('------')
        if rm is not None:
            rgbps, rretr = rm.groups()
        else:
            rgbps = rretr = '-'
        print(f'{fromh} IN:  {rgbps} (retr: {rretr})')


def run_test():
    s = start_servers()
    time.sleep(3)
    try:
        speedtest()
        stop_servers(s)
    except:
        estop()
        raise

if __name__ == '__main__':
    run_test()