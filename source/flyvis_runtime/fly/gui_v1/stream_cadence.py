"""Display-only deadlines: missed display slots never skip neural steps."""
import math
from live_protocol import require

class DisplayCadence:
    def init__(self,hz=15):
        require(type(hz) is int and 1<=hz<=20,'DISPLAY_CADENCE_BOUND')
        self.period=1/hz;self.next_due=0.
    def due(self,elapsed):return elapsed>=self.next_due
    def published(self,elapsed):
        self.next_due=(math.floor(elapsed/self.period)+1)*self.period
