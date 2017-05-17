#!/usr/bin/env python3

import subprocess, sys, os, socket, signal, json, fcntl
import urllib.request, urllib.error



def edit_hosts():
	f = os.popen('/usr/local/bin/etcdctl ls --sort --recursive /hosts')
	hosts_str = f.read()


	hosts_arr = hosts_str.strip('\n').split('\n')
	hosts_fd = open('/tmp/hosts', 'w')

	fcntl.flock(hosts_fd.fileno(), fcntl.LOCK_EX)

	hosts_fd.write('127.0.0.1 localhost cluster' + '\n')
	i = 0
	for host_ip in hosts_arr:
		host_ip = host_ip[host_ip.rfind('/') + 1:]
		if host_ip[0] == '0':
			hosts_fd.write(host_ip[1:] + ' cluster-' + str(i) + '\n')
		else:
			hosts_fd.write(host_ip + ' cluster-' + str(i) + '\n')
		i += 1

	hosts_fd.flush()
	os.system('/bin/cp /tmp/hosts /etc/hosts')
	hosts_fd.close()


def main(ip_addr):
	action = os.getenv('ETCD_WATCH_ACTION')

	stats_url = 'http://127.0.0.1:2379/v2/stats/self'
	stats_request = urllib.request.Request(stats_url)

	stats_reponse = urllib.request.urlopen(stats_request)
	stats_json = stats_reponse.read().decode('utf-8')
	data = json.loads(stats_json)

	print('[INFO] Processing', action)

	if action == 'expire':
		if data['state'] == 'StateLeader':
			os.system('/usr/local/bin/etcdctl mk /hosts/0' + ip_addr + ' ' + ip_addr)
			os.system('/usr/local/bin/etcdctl updatedir --ttl 30 /hosts')

	elif action == 'create':
		edit_hosts()
		if data['state'] == 'StateFollower':
			os.system('/usr/local/bin/etcdctl mk /hosts/' + ip_addr + ' ' + ip_addr)

if __name__ == '__main__':
	main(sys.argv[1])