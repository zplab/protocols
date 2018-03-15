import socket
import time
import itertools

TIMEOUT = 30
HOSTS = ['wustl.edu', 'google.com', 'example.com']

def main():
    hosts = itertools.cycle(HOSTS)
    t0 = time.time()
    for host in hosts:
        t = time.time()
        elapsed = t - t0
        if elapsed > TIMEOUT:
            break
        try:
            socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
            print('Resolved {} at t = {}'.format(host, elapsed))
            break
        except socket.gaierror:
            print('Could not resolve {} at t = {}'.format(host, elapsed))
        time.sleep(0.25)
        t = time.time()

if __name__ == '__main__':
    main()
