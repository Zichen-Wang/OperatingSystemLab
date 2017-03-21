#!/usr/bin/env python2.7
from __future__ import print_function

import sys
import uuid
import time
import socket
import signal
import getpass
from threading import Thread
from os.path import abspath, join, dirname

from pymesos import MesosSchedulerDriver, Scheduler, encode_data, decode_data
from addict import Dict


# executor resources
EXECUTOR_CPUS = 1
EXECUTOR_MEM = 1024

# task resources
TASK_CPU = 0.1
TASK_MEM = 150
TASK_NUM = 10

FILE_PATH = '/home/wzc/Desktop/number.txt'

class GetSumScheduler(Scheduler):
	"""docstring for GetSumScheduler"""

	def __init__(self, executor):
		self.executor = executor
		self.data_split = self.initData()
		self.launched_task = 0
		self.finished_task = 0
		self.result = 0

	def output(self):
		print('[INFO] The total sum is %d' % self.result)

	def initData(self):
		f = open(FILE_PATH, 'r')
		dataset = f.read().split(' ')
		f.close()

		data_split = [''] * TASK_NUM;
		length = max(1, int(len(dataset) / TASK_NUM))

		for x in xrange(TASK_NUM - 1):
			if x * length < len(dataset):
				data_split[x] = ' '.join(dataset[x * length: min(len(dataset), (x + 1) * length)])

		if (TASK_NUM - 1) * length < len(dataset):
			data_split[TASK_NUM - 1] = ' '.join(dataset[(TASK_NUM - 1) * length: len(dataset)])

		return data_split

	def resourceOffers(self, driver, offers):
		filters = {'refuse_seconds': 5}

		for offer in offers:

			if self.launched_task == TASK_NUM:
				return

			cpus = self.getResource(offer.resources, 'cpus')
			mem = self.getResource(offer.resources, 'mem')
			if cpus < TASK_CPU or mem < TASK_MEM:
				continue

			task = Dict()
			task_id = str(uuid.uuid4())
			task.task_id.value = task_id
			task.agent_id.value = offer.agent_id.value
			task.name = 'task {}'.format(task_id)
			task.executor = self.executor
			# send data to executor
			task.data = encode_data(self.data_split[self.launched_task])

			task.resources = [
				dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
				dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
			]

			self.launched_task += 1
			driver.launchTasks(offer.id, [task], filters)

	# receive the result from executor
	def frameworkMessage(self, driver, executorId, slaveId, message):
		self.result += int(decode_data(message))

	def getResource(self, res, name):
		for r in res:
			if r.name == name:
				return r.scalar.value
		return 0.0

	def statusUpdate(self, driver, update):
		# print info of status
		logging.debug('Status update TID %s %s',
					  update.task_id.value,
					  update.state)
		# all tasks have been finished; exit the scheduler
		if update.state == 'TASK_FINISHED':
			self.finished_task += 1
			if self.finished_task == TASK_NUM:
				self.output()
				print('[INFO] All tasks have been finished!')
				exit(0)


def main(master):

	# init executor
	executor = Dict()
	executor.executor_id.value = 'GetSumExecutor'
	executor.name = executor.executor_id.value
	executor.command.value = '%s %s' % (
		sys.executable,
		abspath(join(dirname(__file__), 'executor.py'))
	)
	executor.resources = [
		dict(name = 'mem', type='SCALAR', scalar = {'value': EXECUTOR_MEM}),
		dict(name = 'cpus', type='SCALAR', scalar = {'value': EXECUTOR_CPUS}),
	]

	# init framework
	framework = Dict()
	framework.user = getpass.getuser()
	framework.name = "GetSumFramework"
	framework.hostname = socket.gethostname();


	# init driver
	driver = MesosSchedulerDriver(
		GetSumScheduler(executor),
		framework,
		master,
		use_addict = True,
	)

	# add signal_handler, listen Ctrl + C
	def signal_handler(signal, frame):
		driver.stop()

	def run_driver_thread():
		driver.run()

	# init a thread and start it
	driver_thread = Thread(target = run_driver_thread, args = ())
	driver_thread.start()

	# print info of scheduler
	print('Scheduler running, Ctrl+C to quit.')
	signal.signal(signal.SIGINT, signal_handler)

	while driver_thread.is_alive():
		time.sleep(1)


if __name__ == '__main__':
	import logging
	logging.basicConfig(level = logging.DEBUG)
	if len(sys.argv) != 2:
		print("Usage: {} <mesos_master>".format(sys.argv[0]))
		sys.exit(1)
	else:
		main(sys.argv[1])
