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

