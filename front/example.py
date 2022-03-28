import threading

import cv2
from threading import Thread
from engagement_detect import predict


class NetCore(threading.Thread):

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.running = True
        self.nowAttention = ""

    def getAttention(self):
        return self.nowAttention

    def run(self):
        index = 0
        frames = list()
        while self.running:
            _, frame = self.cap.read()

            if frame is None:
                break
            # 隔20帧采样
            if index % 20 == 0 and len(frames) < 8:
                frames.append(frame)
            # 凑够8帧就开始检测
            elif len(frames) == 8:
                # 这里要用多线程来处理，不然画面会卡
                # t = Thread(target=predict, args=(frames,))
                # t.start()
                level, pos = predict(frames)
                self.nowAttention = str(level)
                print(self.nowAttention)

                frames = list()

            cv2.waitKey(10)
            index += 1


def oldRun():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    frames = list()
    index = 0
    while True:
        _, frame = cap.read()

        if frame is None:
            break
        # 隔20帧采样
        if index % 20 == 0 and len(frames) < 8:
            frames.append(frame)
        # 凑够8帧就开始检测
        elif len(frames) == 8:
            # 这里要用多线程来处理，不然画面会卡
            t = Thread(target=predict, args=(frames,))
            t.start()
            frames = list()

        cv2.imshow('image', frame)
        cv2.waitKey(10)
        index += 1


core = NetCore()
if __name__ == '__main__':
    core.start()


def runCoreThread():
    core.start()


def getNowAttention():
    return core.getAttention()
