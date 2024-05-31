import threading

counter = 0  # 共享资源
lock = threading.Lock()  # 创建一个共享的锁


def increment():
    global counter
    for _ in range(1000):
        with lock:  # 获取线程锁
            counter += 1


threads = [threading.Thread(target=increment) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(counter)  # 输出应该是10000000

import random

# 生成0到3之间的随机整数
random_number = random.randint(0, 3)
print(random_number)
