#!/usr/bin/env python3

import subprocess, sys, os, socket, signal, json, time
import urllib.request, urllib.error
import http.client

def signal_handler(signal, frame):
	global last_pid, last_master
	if last_master != -1:
		last_pid.kill()

	sys.exit(0)



def main():

	global last_pid, last_master
	ip_addr = '172.16.6.251'

	last_master = -1

	signal.signal(signal.SIGINT, signal_handler)

	while True:

		for i in range(5):
			stats_url = 'http://192.168.0.10' + str(i) + ':2379/v2/stats/self'
			stats_request = urllib.request.Request(stats_url)
			try:
				stats_reponse = urllib.request.urlopen(stats_request, timeout = 2)
			except (urllib.error.URLError, socket.timeout):
				print('[INFO] Node 192.168.0.10' + str(i), 'is not running on this host')
			else:
				stats_json = stats_reponse.read().decode('utf-8')
				data = json.loads(stats_json)
				if data['state'] == 'StateLeader':
					print('[INFO] Have found master: 192.168.0.10' + str(i))
					if last_master != i:

						if last_master != -1:
							last_pid.kill()

						args = ['/usr/local/bin/configurable-http-proxy', \
						'--default-target=http://192.168.0.10' + str(i) + ':8888', \
						'--ip=' + ip_addr, '--port=8888']
						last_pid = subprocess.Popen(args)
						last_master = i

					else:
						print('[INFO] Master has not changed')

		stats_url = 'http://172.16.6.24:8888'
		stats_request = urllib.request.Request(stats_url)
		try:
			stats_reponse = urllib.request.urlopen(stats_request, timeout = 2)
		except (urllib.error.URLError, http.client.RemoteDisconnected, socket.timeout):
			print('[INFO] Master is not running on host 172.16.6.24')
		else:
			print('[INFO] Have found master on: 172.16.6.24')
			if last_master != 5:

				if last_master != -1:
					last_pid.kill()

				args = ['/usr/local/bin/configurable-http-proxy', \
				'--default-target=http://172.16.6.24:8888', \
				'--ip=' + ip_addr, '--port=8888']
				last_pid = subprocess.Popen(args)
				last_master = 5



		stats_url = 'http://172.16.6.8:8888'
		stats_request = urllib.request.Request(stats_url)
		try:
			stats_reponse = urllib.request.urlopen(stats_request, timeout = 2)
		except (urllib.error.URLError, http.client.RemoteDisconnected, socket.timeout) as e:
			print('[INFO] Master is not running on host 172.16.6.8')
		else:
			print('[INFO] Have found master on: 172.16.6.8')
			if last_master != 6:

				if last_master != -1:
					last_pid.kill()

				args = ['/usr/local/bin/configurable-http-proxy', \
				'--default-target=http://172.16.6.8:8888', \
				'--ip=' + ip_addr, '--port=8888']
				last_pid = subprocess.Popen(args)
				last_master = 6


		sys.stdout.flush()
		time.sleep(5)



if __name__ == '__main__':
	main()