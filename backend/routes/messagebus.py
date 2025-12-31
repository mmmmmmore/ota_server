# backend/messagebus.py
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

class MessageBus:
    def __init__(self, default_ttl=10, max_workers = 10):
        """
        default_ttl: 消息的默认生命周期（秒）
        """
        self.subscribers = defaultdict(list)   # event_type -> [handlers]
        self.messages = defaultdict(list)      # event_type -> [(payload, expire_time)]
        self.lock = threading.Lock()
        self.default_ttl = default_ttl
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def subscribe(self, event_type, handler, consume_old=True):
        """
        注册订阅者
        - event_type: 消息类型
        - handler: 回调函数
        - consume_old: 是否消费缓存的旧消息
        """
        with self.lock:
            self.subscribers[event_type].append(handler)
            if consume_old and event_type in self.messages:
                now = time.time()
                valid_msgs = []
                for payload, expire in self.messages[event_type]:
                    if expire > now:
                        # 立即触发回调
                        try:
                            handler(payload)
                        except Exception as e:
                            print(f"[Bus] handler error: {e}")
                        valid_msgs.append((payload, expire))
                # 更新缓存（只保留未过期的）
                self.messages[event_type] = valid_msgs

    def publish(self, event_type, payload, ttl=None):
        """
        发布消息
        - event_type: 消息类型
        - payload: 消息内容
        - ttl: 生命周期（秒）
        """
        expire_time = time.time() + (ttl or self.default_ttl)
        with self.lock:
            handlers = self.subscribers.get(event_type, [])
            
            if handlers:
                #  create payload to async thread pool
                for handler in handlers:
                    print("[Msg_BUS]", handler)
                    self.executor.submit(self._safe_invoke, handler, payload)
                    #print(self.messages)
            else:
                # 没有订阅者 → 缓存消息
                self.messages.setdefault(event_type, []).append((payload, expire_time))

        # 启动定时器清理过期消息
        threading.Timer(ttl or self.default_ttl, self._cleanup, args=[event_type]).start()

    def _safe_invoke(self, handler, payload):
        try:
            print("[Msg_BUS]",handler)
            print("[Msg_BUS]",payload)
            handler(payload)
        except Exception as e:
            print(f"[MsgBus] handler error: {e}")

    def _cleanup(self, event_type):
        """清理过期消息"""
        with self.lock:
            now = time.time()
            if event_type in self.messages:
                self.messages[event_type] = [
                    (payload, expire) for payload, expire in self.messages[event_type]
                    if expire > now
                ]

# 全局单例
bus = MessageBus(default_ttl=15)
