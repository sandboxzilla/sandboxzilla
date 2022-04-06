#!/bin/python3
#
#  Copyright (c) 2019-2021.  SandboxZilla
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this
#  software and associated documentation files (the "Software"), to deal in the Software
#  without restriction, including without limitation the rights to use, copy, modify,
#  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
#  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#

__author__ = 'Erol Yesin'
from typing import Any


class EventHandler(object):

    def __init__(self, **kwargs):
        """
        The __init__ function is called when an instance of the EVentHandler is created.
        Used to initialize the instance.

        The **kwargs is a dictionary that contains the arguments passed to the function.
        The cb_routines dictionary is used to store the callback routines.
        """
        # packet is the token passed to the subscriber callbacks
        self.packet = kwargs
        # src key holds the event id.  It should be passed in when instantiated
        assert 'src' in self.packet, "src key not defined"
        # Minimum required keys in the packet dictionary
        if 'dest' not in self.packet:
            self.packet['dest'] = None
        if 'payload' not in self.packet:
            self.packet['payload'] = None
        if 'cookie' not in self.packet:
            self.packet['cookie'] = None
        # super(EventHandler, self).__init__(**self.packet)
        self.cb_routines = {}

    def subscribe(self, name: str, on_event: callable, cookie: Any = None):
        if name not in self.cb_routines:
            self.cb_routines[name] = {'on_event': on_event, 'cookie': cookie}
        return self

    def unsubscribe(self, name):
        """
        The unsubscribe function is used to remove a callback routine from the list of routines that are called when an event is triggered.
        The unsubscribe function takes one argument, which is the name of the callback routine to be removed.

        :param name: Subscriber ID.  Used to Delete the subscriber from the list of subscribers.
        :return: the EventHandler instance.  Allows chaining

        :doc-author: Trelent
        """
        if name in self.cb_routines:
            del self.cb_routines[name]
        return self

    def post(self, payload, **kwargs):
        packet = self.packet.copy()
        for field in kwargs:
            packet[field] = kwargs[field]
        packet['payload'] = payload
        for name, cb_routine in self.cb_routines.copy().items():
            packet['dest'] = name
            # noinspection PyUnresolvedReferences
            packet['cookie'] = cb_routine['cookie']
            # noinspection PyUnresolvedReferences
            cb_routine['on_event'](packet)
        return self

    def __call__(self, payload, **kwargs):
        return self.post(payload=payload, **kwargs)
