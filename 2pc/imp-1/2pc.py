'''
Implementation of 2 Phase Commit as explained at Wikipedia:
https://en.wikipedia.org/wiki/Two-phase_commit_protocol
'''
import random, logging, time
from threading import Thread, Semaphore, Lock

_fmt = '%(user)s:%(levelname)s >>> %(message)s'
logging.basicConfig(format=_fmt)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

MIN_ACCOUNT = 0
MAX_ACCOUNT = 100
NO_COHORTS = 2


class Coordinator(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.start_sem = Semaphore(0)
		self.cohorts = []
		self.votes = []
		self.acks = []
		self._log_extra = dict(user='COORD')

	def yes(self):
		self.votes.append(True)

	def no(self):
		self.votes.append(False)

	def ack(self):
		self.acks.append(True)

	def start_voting(self, cohort):
		self.cohorts.append(cohort)
		self.start_sem.release()

	def run(self):
		self.start_sem.acquire(NO_COHORTS)

		## Voting Phase:
		# 1. The coordinator sends a query to commit message to all cohorts and
		# waits until it has received a reply from all cohorts.
		for cohort in self.cohorts:
			LOG.info('query_to_commit to {}'.format(cohort.uname), extra=self._log_extra)
			cohort.query_to_commit()

		## Commit Phase:
		# If the coordinator received an agreement message from all cohorts
		# during the commit-request phase
		if all(self.votes):
			# 1. The coordinator sends a commit message to all the cohorts.
			LOG.info('Committing', extra=self._log_extra)
			for cohort in self.cohorts:
				cohort.commit()
		# If any cohort votes No during the commit-request phase (or the
		# coordinator's timeout expires)
		else:
			# 1. The coordinator sends a rollback message to all the cohorts.
			LOG.warning('Rolling back', extra=self._log_extra)
			for cohort in self.cohorts:
				cohort.rollback()

		if all(self.acks):
			LOG.info('END', extra=self._log_extra)
		else:
			LOG.error('KO something went wrong while receiving acks', extra=self._log_extra)

		for cohort in self.cohorts:
			cohort.end()


class Cohort(Thread):
	def __init__(self, uname, coord):
		Thread.__init__(self)
		self.uname = uname
		self.coord = coord
		self.do = None
		self.undo = None
		self.sem = Semaphore(0)
		self.lock = Lock()
		self.account = random.randint(MIN_ACCOUNT, MAX_ACCOUNT)
		self._log_extra = dict(user=uname)

	def query_to_commit(self):
		## Voting phase:
		# 3. Each cohort replies with an agreement message (cohort votes Yes to
		# commit), if the cohort's actions succeeded, or an abort message
		# (cohort votes No, not to commit), if the cohort experiences a failure
		# that will make it impossible to commit.
		if self.res:
			LOG.info('vote YES', extra=self._log_extra)
			self.coord.yes()
		else:
			LOG.info('vote NO', extra=self._log_extra)
			self.coord.no()

	def commit(self):
		self.commit = True

	def rollback(self):
		self.commit = False

	def end(self):
		self.sem.release()

	def run(self):
		LOG.debug('BEFORE {}'.format(self.account), extra=self._log_extra)

		# executing operation and saving result
		self.lock.acquire()

		# LOG.debug('?? {}'.format(self.do), extra=self._log_extra)

		## Voting phase:
		# 2. The cohorts execute the transaction up to the point where they
		# will be asked to commit. They each write an entry to their undo log
		# and an entry to their redo log.
		for do in self.do:
			do()

		self.res = self.account >= MIN_ACCOUNT and self.account <= MAX_ACCOUNT
		self.coord.start_voting(self)

		LOG.debug('DURING {}'.format(self.account), extra=self._log_extra)

		# waiting for the end of voting phase
		LOG.debug('going to sleep', extra=self._log_extra)
		self.sem.acquire()
		LOG.debug('awaken', extra=self._log_extra)
		## Commit phase:
		if self.commit:
			# 2. Each cohort completes the operation ...
			LOG.info('commit', extra=self._log_extra)
		else:
			# 2. Each cohort undoes the transaction using the undo log ...
			for undo in self.undo:
				undo()
			LOG.info('rollback', extra=self._log_extra)
		# 2. ... and releases all the locks and resources held during the
		# transaction.
		self.lock.release()

		# 3. Each cohort sends an acknowledgment to the coordinator.
		self.coord.ack()

		LOG.debug('AFTER {}'.format(self.account), extra=self._log_extra)


if __name__ == '__main__':
	coord = Coordinator()
	u1 = Cohort('user1', coord)
	u2 = Cohort('user2', coord)

	amount = random.randint(MIN_ACCOUNT, MAX_ACCOUNT)
	LOG.info("amount = " + str(amount), extra=dict(user='main'))


	def u1_do():
		u1.account -= amount


	def u1_undo():
		u1.account += amount


	def u2_do():
		u2.account += amount


	def u2_undo():
		u2.account -= amount


	u1.do = [u1_do, ]
	u2.do = [u2_do, ]
	u1.undo = [u1_undo, ]
	u2.undo = [u2_undo, ]

	coord.start()
	u1.start()
	u2.start()

	u2.join()
	u1.join()
	coord.join()
