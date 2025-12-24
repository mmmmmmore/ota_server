import threading
import time
from collections import defaultdict


class MessageBus:
    def __init__(self, default_ttl = 10):
        self.subscribers = defaultdict(list)
        self.messages = defaultdict(list)
        self.lock = threading.Lock()
        self.default_ttl  = default_ttl
        
    
    def subscribe(self, event_type, handler, consume_old= True):
        pass
    
    