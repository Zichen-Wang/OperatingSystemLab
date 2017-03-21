#!/usr/bin/env python2.7
from __future__ import print_function

import sys
import time
from threading import Thread

from pymesos import MesosExecutorDriver, Executor, encode_data, decode_data
from addict import Dict


class GetSumExecutor(Executor):
	def launchTask(self, driver, task):
		def run_task(task):
			update = Dict()
			update.task_id.value = task.task_id.value
			update.state = 'TASK_RUNNING'
			update.timestamp = time.time()
			driver.sendStatusUpdate(update)

			data = decode_data(task.data).split(' ')
			result = 0
			for x in data:
				if x != '':
					result += int(x)

			# send the result to the scheduler
			driver.sendFrameworkMessage(encode_data(str(result)))

			update = Dict()
			update.task_id.value = task.task_id.value
			update.state = 'TASK_FINISHED'
			update.timestamp = time.time()
			driver.sendStatusUpdate(update)

		thread = Thread(target=run_task, args=(task,))
		thread.start()


if __name__ == '__main__':
	import logging
	logging.basicConfig(level=logging.DEBUG)
	driver = MesosExecutorDriver(GetSumExecutor(), use_addict=True)
	driver.run()
