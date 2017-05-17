#!/usr/bin/env python3

import subprocess, sys, os, socket, signal, json, time
import urllib.request, urllib.error



def start_ssh():
	os.system('ssh-keygen -f /home/admin/.ssh/id_rsa -t rsa -N ""')
	os.system('echo "admin" | sudo -S bash -c "cat /home/admin/.ssh/id_rsa.pub >> /ssh_info/authorized_keys"')
	os.system('/usr/sbin/service ssh start')

def start_etcd(ip_addr):

	args = ['/usr/local/bin/etcd', '--name', 'node' + ip_addr[-1], \
	'--data-dir', '/var/lib/etcd', \
	'--initial-advertise-peer-urls', 'http://' + ip_addr + ':2380', \
	'--listen-peer-urls', 'http://' + ip_addr + ':2380', \
	'--listen-client-urls', 'http://' + ip_addr + ':2379,http://127.0.0.1:2379', \
	'--advertise-client-urls', 'http://' + ip_addr + ':2379', \
	'--initial-cluster-token', 'etcd-cluster-hw6', \
	'--initial-cluster', 'node0=http://192.168.0.100:2380,node1=http://192.168.0.101:2380,node2=http://192.168.0.102:2380,node3=http://192.168.0.103:2380,node4=http://192.168.0.104:2380', \
	'--initial-cluster-state', 'new']
	subprocess.Popen(args)


def watch_dog(ip_addr):
	args = ['/usr/local/bin/etcdctl', 'exec-watch', '--recursive', '/hosts', '--', '/usr/bin/python3', '/home/admin/code/watch.py', ip_addr]
	subprocess.Popen(args)

def main():

	f = os.popen("ifconfig cali0 | grep 'inet addr' | cut -d ':' -f 2 | cut -d ' ' -f 1")
	ip_addr = f.read().strip('\n')

	start_ssh()
	start_etcd(ip_addr)

	leader_flag = 0
	watch_flag = 0
	stats_url = 'http://127.0.0.1:2379/v2/stats/self'
	stats_request = urllib.request.Request(stats_url)
	while True:
		try:
			stats_reponse = urllib.request.urlopen(stats_request)
		except urllib.error.URLError as e:
			print('[WARN] ', e.reason)
			print('[WARN] Wating etcd...')

		else:
			if watch_flag == 0:
				watch_flag = 1
				watch_dog(ip_addr)

			stats_json = stats_reponse.read().decode('utf-8')
			data = json.loads(stats_json)


			if data['state'] == 'StateLeader':
				if leader_flag == 0:
					leader_flag = 1

					args = ['/usr/local/bin/jupyter', 'notebook', '--NotebookApp.token=', '--ip=0.0.0.0', '--port=8888']
					subprocess.Popen(args)

					os.system('/usr/local/bin/etcdctl rm /hosts')
					os.system('/usr/local/bin/etcdctl mk /hosts/0' + ip_addr + ' ' + ip_addr)
					os.system('/usr/local/bin/etcdctl updatedir --ttl 30 /hosts')
				else:
					os.system('/usr/local/bin/etcdctl mk /hosts/0' + ip_addr + ' ' + ip_addr)


			elif data['state'] == 'StateFollower':
				leader_flag = 0
				os.system('/usr/local/bin/etcdctl mk /hosts/' + ip_addr + ' ' + ip_addr)

		time.sleep(1)


if __name__ == '__main__':
	main()