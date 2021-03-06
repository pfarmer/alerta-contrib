import time
import threading
import logging

LOG = logging.getLogger(__name__)
lock = threading.Lock()

TOKEN_LIMIT = 20
TOKEN_RATE = 2


class LeakyBucket(threading.Thread):

    def __init__(self, tokens=None, limit=None, rate=None):

        self.tokens = tokens or TOKEN_LIMIT
        self.limit = limit or tokens or TOKEN_LIMIT
        self.rate = rate or TOKEN_RATE

        threading.Thread.__init__(self)

        self.running = False
        self.shuttingdown = False

    def shutdown(self):

        self.shuttingdown = True

        if not self.running:
            return
        self.join()

    def run(self):

        self.running = True

        while not self.shuttingdown:

            if self.shuttingdown:
                break

            if self.tokens < self.limit:
                with lock:
                    self.tokens += 1
                LOG.debug('Token top-up! Now %s tokens', self.tokens)

            if not self.shuttingdown:
                time.sleep(self.rate)

        self.running = False

    def is_token(self):
        if self.tokens > 0:
            return True
        else:
            return False

    def get_token(self):
        with lock:
            if self.is_token():
                self.tokens -= 1
                LOG.debug('Got a token! There are %s left', self.tokens)
                return True
            else:
                LOG.debug('Sorry, no tokens left')
                return False

    def get_count(self):
        return self.tokens