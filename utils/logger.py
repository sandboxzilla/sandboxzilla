#!/bin/python3

#  Copyright (c)  2018-2022.  Sandboxzilla
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this
#  software and associated documentation files (the "Software"), to deal in the Software
#  without restriction, including without limitation the rights to use, copy, modify,
#  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#   INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#   PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#   HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
#   OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#   SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


__author__ = 'Erol Yesin'

import sys
import time
import logging
from logging.handlers import MemoryHandler
from pathlib import PosixPath

VER = '0.8'


class LoggerWrapper(logging.Logger):
    __instance = None

    def __new__(cls,
                name: str,
                level: int = None,
                show_level: bool = True,
                show_thread: bool = True,
                show_module: bool = True,
                show_method: bool = True,
                date_filename: bool = True,
                console_output: bool = True,
                handlers: logging.handlers = None,
                handler_name: str = None) -> logging.Logger:
        if LoggerWrapper.__instance is None:

            name = PosixPath(name).expanduser()

            if len(name.suffix) == 0:
                name = PosixPath(str(name) + ".utils")
            sfx = name.suffix

            location = name.parent
            name = PosixPath(name.name)

            if len(str(location)) <= 1:
                location = PosixPath("~/logs").expanduser()

            if not location.exists():
                location.mkdir()

            LoggerWrapper.__instance = logging.getLogger(name=name.stem)
            LoggerWrapper.__instance.location = location

            if date_filename:
                file_obj = PosixPath(location, name.stem() + time.strftime("_%Y%m%d%H%M%S" + sfx))
            else:
                file_obj = PosixPath(location, name)

            if level is None:
                level = logging.DEBUG

            format_str = '%(asctime)s.%(msecs)03d,'
            if show_level:
                format_str += '[%(levelname)s],'
            if show_module or show_method or show_thread:
                format_str += '['
                if show_thread:
                    format_str += '%(threadName)s'
                if show_module:
                    format_str += ':%(module)s'
                if show_method:
                    format_str += ':%(funcName)s'
                if show_module:
                    format_str += ':%(lineno)d'
                format_str += '],'

            LoggerWrapper.__instance.setLevel(level=level)
            LoggerWrapper.__instance.name = name
            LoggerWrapper.__instance.formatter = logging.Formatter(format_str + '%(message)s')

            if LoggerWrapper.__instance.hasHandlers():
                LoggerWrapper.__instance.handlers.clear()

            if console_output:
                stream_handler = logging.StreamHandler()
                stream_handler.set_name(name=name)
                stream_handler.setFormatter(LoggerWrapper.__instance.formatter)
                LoggerWrapper.__instance.addHandler(stream_handler)

            file_handler = logging.FileHandler(file_obj)
            file_handler.set_name(name=name)
            file_handler.setFormatter(LoggerWrapper.__instance.formatter)
            LoggerWrapper.__instance.addHandler(file_handler)

        LoggerWrapper.__instance.date_filename = date_filename
        LoggerWrapper.__instance.add_file_handler = cls.add_file_handler
        LoggerWrapper.__instance.remove_handler = cls.remove_handler
        LoggerWrapper.__instance.version = cls.version

        if handlers is not None:
            for handler in handlers:
                if isinstance(handler, logging.Handler):
                    LoggerWrapper.__instance.addHandler(handler)

        if handler_name is not None:
            cls.add_file_handler(log=LoggerWrapper.__instance, name=handler_name)

        return LoggerWrapper.__instance

    @staticmethod
    def add_file_handler(log, name):
        for index, handler in enumerate(log.handlers):
            if name in handler.name:
                return handler
        if log.date_filename:
            file_obj = PosixPath(log.location, name + time.strftime("_%Y%m%d%H%M%S.utils"))
        else:
            file_obj = PosixPath(log.location, name + ".utils")
        handler = logging.FileHandler(file_obj)
        handler.set_name(name=name)
        handler.setFormatter(log.formatter)
        log.addHandler(handler)
        return handler

    @staticmethod
    def remove_handler(log, name):
        for index, handler in enumerate(log.handlers):
            if handler.name == name:
                log.removeHandler(handler)

    @property
    def version(self):
        return VER


def log_on_error(logger=None, capacity=None):
    if logger is None:
        logger = LoggerWrapper()

    if capacity is None:
        capacity = 100
    mem_handler = MemoryHandler(capacity, flushLevel=logger.level)
    for handler in logger.handlers:
        mem_handler.setTarget(handler)
    logger.addHandler(mem_handler)

    def decorator(fn):
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except KeyboardInterrupt:
                logger.info('Stopping...')
                sys.exit(0)
            except Exception as exp:
                logger.exception('Call Failed', exc_info=exp)
                sys.exit(0)
            finally:
                super(MemoryHandler, mem_handler).flush()
                logger.removeHandler(mem_handler)

        return wrapper

    return decorator
