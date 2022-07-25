import sys
import os
import time
import traceback

import Environment

from PyQt5.QtCore import QT_VERSION_STR, qInstallMessageHandler, Qt, QCoreApplication
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterType
from asyncqt import QEventLoop
import asyncio
from EventLoop import EventLoop


application_path = (
    os.path.dirname(sys.executable)
    if getattr(sys, "frozen", False)
    else os.path.dirname(os.path.abspath(__file__))
)


def qt_message_handler(mode, context, message):
    print(message)


running = True


async def main_processing():
    global running

    while running:
        await asyncio.sleep(1)


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    qInstallMessageHandler(qt_message_handler)

    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    ev = EventLoop(app)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    ctx = engine.rootContext()
    qmlRegisterType(Environment.Environment, 'Environment', 1, 0, 'Environment')
    engine.load(os.path.join(application_path, "qml/app.qml"))

    with loop:
        loop.run_until_complete(ev.run())

    app.exit(0)
