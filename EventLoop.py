from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject
import asyncio
import traceback


def invoke_repeating(func, time):
    async def do_func_repeating():
        while True:
            await asyncio.sleep(time)
            try:
                func()
            except BaseException as e:
                print(''.join(traceback.format_tb(e.__traceback__)))
                print(e)

    return asyncio.create_task(do_func_repeating())


def invoke(func, time):
    async def do_func():
        await asyncio.sleep(time)
        try:
            func()
        except BaseException as e:
            print(''.join(traceback.format_tb(e.__traceback__)))
            print(e)

    return asyncio.create_task(do_func())


class Task:
    def __init__(self, func, trigger_time, repeat):
        self.func = func
        self.trigger_time = trigger_time
        self.repeat = repeat

        self.current_time = 0.0

    def check(self, dt):
        self.current_time += dt
        if self.current_time >= self.trigger_time:
            self.func()
            self.current_time -= self.trigger_time

            return True

        return False


class SynchronousEventLoop:
    def __init__(self):
        self.tasks = []

    def update(self, delta_time: float):
        for task in self.tasks[:]:
            if task.check(delta_time):
                if not task.repeat:
                    self.tasks.remove(task)

    def invoke_repeating(self, func, time):
        self.tasks.append(Task(func, time, True))

    def invoke(self, func, time):
        self.tasks.append(Task(func, time, False))


class EventLoop(QObject):
    def __init__(self, app: QApplication):
        super().__init__()
        self.running = True

        self._app = app

        app.setQuitOnLastWindowClosed(False)
        app.lastWindowClosed.connect(self.close)

    def close(self):
        if len(self._app.allWindows()) == 1:
            self.running = False

    async def run(self):
        while self.running:
            await asyncio.sleep(1)

