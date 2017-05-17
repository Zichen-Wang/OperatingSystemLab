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

TASK_CPU = 0.2
TASK_MEM = 128
TASK_NUM = 5



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
			# ip
			ip = Dict()
			ip.key = 'ip'
			ip.value = '192.168.0.10' + str(self.launched_task)

			# hostname
			hostname = Dict()
			hostname.key = 'hostname'
			hostname.value = 'cluster'

			# volume1
			volume1 = Dict()
			volume1.key = 'volume'
			volume1.value = '/home/pkusei/hw6/ssh_docker:/ssh_info'

			# volume2
			volume2 = Dict()
			volume2.key = 'volume'
			volume2.value = '/home/pkusei/hw6/data_docker:/home/admin/shared_folder'


			# NetworkInfo
			NetworkInfo = Dict()
			NetworkInfo.name = 'my_net'

			# DockerInfo
			DockerInfo = Dict()
			DockerInfo.image = 'ubuntu_jupyter_etcd'
			DockerInfo.network = 'USER'
			DockerInfo.parameters = [ip, hostname, volume1, volume2]

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
			task.name = 'Docker task'
			task.container = ContainerInfo
			task.command = CommandInfo

			task.resources = [
				dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
				dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
			]

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
	if len(sys.argv) < 2:
		print("Usage: {} <mesos_master>".format(sys.argv[0]))
		sys.exit(1)
	else:
		main(sys.argv[1])
