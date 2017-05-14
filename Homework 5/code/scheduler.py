#!/usr/bin/env python2.7
from __future__ import print_function

import subprocess
import sys
import os
import uuid
import time
import socket
import signal
import getpass
from threading import Thread
from os.path import abspath, join, dirname

from pymesos import MesosSchedulerDriver, Scheduler, encode_data
from addict import Dict

TASK_CPU = 0.1
TASK_MEM = 128
TASK_NUM = 5

agent_map = Dict()


class DockerJupyterScheduler(Scheduler):

	def __init__(self):
		self.launched_task = 0

	def resourceOffers(self, driver, offers):
		filters = {'refuse_seconds': 5}

		for offer in offers:
			cpus = self.getResource(offer.resources, 'cpus')
			mem = self.getResource(offer.resources, 'mem')
			if self.launched_task == TASK_NUM:
				return
			if cpus < TASK_CPU or mem < TASK_MEM:
				continue

			# Launching tasks
			if self.launched_task == 0:
				# ip
				ip = Dict()
				ip.key = 'ip'
				ip.value = '192.168.0.100'

				# hostname
				hostname = Dict()
				hostname.key = 'hostname'
				hostname.value = 'cluster'

				# NetworkInfo
				NetworkInfo = Dict()
				NetworkInfo.name = 'my_net'

				# DockerInfo
				DockerInfo = Dict()
				DockerInfo.image = 'ubuntu_jupyter'
				DockerInfo.network = 'USER'
				DockerInfo.parameters = [ip, hostname]

				# ContainerInfo
				ContainerInfo = Dict()
				ContainerInfo.type = 'DOCKER'
				ContainerInfo.docker = DockerInfo
				ContainerInfo.network_infos = [NetworkInfo]

				# CommandInfo
				CommandInfo = Dict()
				CommandInfo.shell = False

				task = Dict()
				task_id = 'node0'
				task.task_id.value = task_id
				task.agent_id.value = offer.agent_id.value
				task.name = 'Docker jupyter task'
				task.container = ContainerInfo
				task.command = CommandInfo

				task.resources = [
					dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
					dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
				]

				print("Launching the jupyter task")

				self.launched_task += 1
				driver.launchTasks(offer.id, [task], filters)

				global agent_map
				num = agent_map[task.agent_id.value]

				http_proxy_log = open('/home/pkusei/hw5/http_proxy.log', 'w')
				args = ['/usr/local/bin/configurable-http-proxy']
				if num == 0:
					args.append('--default-target=http://192.168.0.100:8888')
				elif num == 1:
					args.append('--default-target=http://172.16.6.24:8888')
				else:
					args.append('--default-target=http://172.16.6.8:8888')

				args.append('--ip=172.16.6.251')
				args.append('--port=8888')

				global http_proxy_pro
				http_proxy_pro = subprocess.Popen(args, stdout=http_proxy_log, stderr=http_proxy_log)

			else:
				# ip
				ip = Dict()
				ip.key = 'ip'
				ip.value = '192.168.0.10' + str(self.launched_task)

				# hostname
				hostname = Dict()
				hostname.key = 'hostname'
				hostname.value = 'cluster'

				# NetworkInfo
				NetworkInfo = Dict()
				NetworkInfo.name = 'my_net'

				# DockerInfo
				DockerInfo = Dict()
				DockerInfo.image = 'ubuntu_jupyter_client'
				DockerInfo.network = 'USER'
				DockerInfo.parameters = [ip, hostname]

				# ContainerInfo
				ContainerInfo = Dict()
				ContainerInfo.type = 'DOCKER'
				ContainerInfo.docker = DockerInfo
				ContainerInfo.network_infos = [NetworkInfo]

				# CommandInfo
				CommandInfo = Dict()
				CommandInfo.shell = False

				task = Dict()
				task_id = 'node' + str(self.launched_task)
				task.task_id.value = task_id
				task.agent_id.value = offer.agent_id.value
				task.name = 'Docker normal task'
				task.container = ContainerInfo
				task.command = CommandInfo

				task.resources = [
					dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
					dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
				]

				print("Launching a normal task")

				self.launched_task += 1
				driver.launchTasks(offer.id, [task], filters)


	def getResource(self, res, name):
		for r in res:
			if r.name == name:
				return r.scalar.value
		return 0.0

	def statusUpdate(self, driver, update):
		logging.debug('Status update TID %s %s',
					  update.task_id.value,
					  update.state)


def main(master):

	# Framework info
	framework = Dict()
	framework.user = getpass.getuser()
	framework.name = "DockerJupyterFramework"
	framework.hostname = socket.gethostname()

	# Use default executor
	driver = MesosSchedulerDriver(
		DockerJupyterScheduler(),
		framework,
		master,
		use_addict=True,
	)

	def signal_handler(signal, frame):
		driver.stop()
		global http_proxy_pro
		http_proxy_pro.kill()


	def run_driver_thread():
		driver.run()

	driver_thread = Thread(target=run_driver_thread, args=())
	driver_thread.start()

	print('Scheduler running, Ctrl+C to quit.')
	signal.signal(signal.SIGINT, signal_handler)

	while driver_thread.is_alive():
		time.sleep(1)

if __name__ == '__main__':
	import logging
	logging.basicConfig(level=logging.DEBUG)
	if len(sys.argv) < 4:
		print("Usage: {} <mesos_master> <number of agent> [agent_id ...]".format(sys.argv[0]))
		sys.exit(1)
	else:
		for i in range(int(sys.argv[2])):
			agent_map[sys.argv[3 + i]] = i
		main(sys.argv[1])
