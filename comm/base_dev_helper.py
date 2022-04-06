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
#
from __future__ import absolute_import

__author__ = 'Erol Yesin'

from abc import ABC, abstractmethod
from threading import Thread
from typing import Any, List

from utils import Queue as Q
from utils import EventHandler as Eventer
from utils import LoggerWrapper


# The BaseCommDeviceHelper class is an abstract base class that defines the interface for a CommDeviceHelper
class BaseCommDeviceHelper(ABC):
    EOLL: List[str] = ["\r\n", "\n"]
    EOL = "\r\n"

    def __init__(self,
                 address: str = "Address not defined",
                 recv_proc: callable = None,
                 send_proc: callable = None,
                 dist_proc: callable = None,
                 **kwargs):
        """
        The __init__ function is called when an instance of the class is created.
        It initializes attributes that are specific to each instance, and can take arguments
        that will be passed to the class's methods. In this case, it takes a dictionary of keyword arguments:

            address: The IP address or hostname for the device being connected to. Defaults to "Address not defined" if no value is provided in kwargs

            recv_proc: A function that will process input from a queue and send it out over serial as bytes (or whatever format). If no value is provided in kwargs, defaults to self.__process_input__()

            send_proc: A function that will pull data from a queue and put it into another queue for sending over serial (or whatever format). If no value is provided in kwargs, defaults to self.__process_output__()

            dist_proc: A function that processes input received by recv_proc and puts processed output into __outQ for distribution by send proc.

        :param self: Used to Reference the class instance.
        :param address:str="Address not defined": Used to Set the address of the device.
        :param recv_proc:callable=None: Used to Pass a function to the __init__ function.
        :param send_proc:callable=None: Used to Specify a function that will be called to process the output queue.
        :param dist_proc:callable=None: Used to Define a function that will be called to distribute the input from the inq.
        :param **kwargs: Used to Pass a variable number of arguments to a function.
        :return: The __event dictionary.

        :doc-author: Trelent
        """

        self.name = self.__class__.__name__
        self.RX_EVENT = self.name + 'InEvent'
        self.TX_EVENT = self.name + 'OutEvent'

        self.__dict__.update(kwargs)

        self.__event = {self.RX_EVENT: Eventer(event=self.RX_EVENT, src=self.name),
                        self.TX_EVENT: Eventer(event=self.TX_EVENT, src=self.name)}

        self.__inQ = Q()
        self.__outQ = Q()

        self.timeout = kwargs.get("timeout", 4)
        self.continue_thread = True
        label = self.name[:3].lower()
        if recv_proc is None:
            recv_proc = self.__process_input__
        self.__inT = Thread(name=label + 'IT', target=recv_proc, args=(self.__inQ,))

        if send_proc is None:
            send_proc = self.__process_output__
        self.__outT = Thread(name=label + 'OT', target=send_proc, args=(self.__outQ,))

        if dist_proc is None:
            dist_proc = self.__distribute_input__
        self.__distT = Thread(name=label + 'DT', target=dist_proc)

        self.debug_logger = kwargs.get("debug_logger", None)
        if  any(key in kwargs for key in ("debug_on", "file_name")):
            self.debug_on(**kwargs)
            self.debug_write(topic='START ' + __name__, data=address)

    @classmethod
    @abstractmethod
    def _send(self, data: any):
        """
        The _send function is an internal function that is not meant to be called directly.  It is used by the send()
        method of the Connection class, and it will be populated by classes inheriting from Connection.  The _send function should
        be implemented as a generator, which yields data in chunks until all data has been sent.

        :param self: Used to Reference the object instance of the class.
        :param data:any: Used to Pass any type of data to the send function.
        :return: None.

        :doc-author: Trelent
        """
        pass

    @classmethod
    @abstractmethod
    def _recv(self, size=1024):
        """
        Internal method for reading data.  To be populated by inherited class.
        :param size: int size of read buffer defaults to 1024
        """
        pass
        return ""

    @classmethod
    @abstractmethod
    def _open(self, **kwargs):
        """
        Internal method for opening the communication channel.  To be populated by inherited class.
        :param kwargs: optional parameters passed with keywords.  Implementation dependent
        """
        pass

    @classmethod
    @abstractmethod
    def _close(self):
        pass

    def send(self, data):
        """
        It takes one argument, data, which is the string of data that will be sent.  The function returns nothing.
        Send is the library client facing interface.
        :param data: Used to Send data to the server.

        :doc-author: Trelent
        """
        self.__outQ.put(data)

    def subscribe(self, name: str, call_back: callable, event: str = None, cookie: Any = None):
        """
        The subscribe function allows the caller to register a callback function with
        the event loop. The subscribe function takes two arguments: name and call_back.
        The name argument is a string that uniquely identifies the type of events you
        want your callback function to receive; for example, "button press" or "knob turn."
        The call_back argument is the address of a Python function that you want the
        event loop to call when an event of type name occurs. The subscribe method returns
        a cookie value that can be used later in an unsubscribe() method call.

        :param self: Used to Reference the class instance.
        :param name:str: Used to Specify the name of the subscriber.
        :param call_back:callable: Used to Specify the function that will be called when a message is received.
        :param event:str=None: Used to Specify an event name.
        :param cookie:Any=None: Used to Pass a user-defined object to the callback function.
        :return: A tuple containing the cookie and the event.

        :doc-author: Trelent
        """

        if event is None:
            event = self.RX_EVENT
        self.__event[event].subscribe(name=name, on_event=call_back, cookie=cookie)

    def unsubscribe(self, name: str, event: str = None):
        """
        The unsubscribe function is used to remove a name from an event.
        It takes two arguments, name and event. Name is the name of the subscriber that you want to unsubscribe from an event.
        Event is optional and will default to RX_EVENT if not specified.

        :param name:str: Used to Identify the subscriber.
        :param event:str=None: Used to Specify which event to unsubscribe from.
        :return: None.

        :doc-author: Trelent
        """
        if event is None:
            event = self.RX_EVENT
        self.__event[event].unsubscribe(name=name)

    def start(self, name: str, call_back: callable, event: str = None, cookie: Any = None):
        """
        The start function subscribes the given name to the given event with a call_back function.
        The cookie is used by the subscribing listener for internal purposes.

        :param name:str: Used to identify of the subscriber.
        :param call_back:callable: Used to Specify the function that will be called when an event occurs.
        :param event:str=None: Used to Specify the event to subscribe to.
        :param cookie:Any=None: Used internally by the subscriber.
        :return: self so command can be chained

        :doc-author: Trelent
        """
        if event is None:
            event = self.RX_EVENT
        self.subscribe(name=name, call_back=call_back, event=event, cookie=cookie)
        self.__event[event].post(payload='Start logging topic %s to %s' % (event, name))
        return self

    def stop(self, name: str, event: str = None):
        """
        The stop function stops the event based processing.

        :param name:str: Used to Identify the stop function.
        :param event:str=None: Used to Specify the event to be posted.
        :return: The payload of the event.

        :doc-author: Trelent
        """
        if event is None:
            event = self.RX_EVENT

        self.__event[event].post(payload='Stop logging topic %s to %s' % (event, name))
        self.unsubscribe(event=event, name=name)

    def open(self, **kwargs):
        self.continue_thread = True
        self._open(**kwargs)
        self.__inT.start()
        self.__outT.start()
        self.__distT.start()
        return self

    def close(self):
        self.continue_thread = False
        self._close()
        if self.__inT.is_alive():
            self.__inQ.put(item=None)
            self.__inT.join(timeout=4)
        if self.__outT.is_alive():
            self.__outQ.put(item=None)
            self.__outT.join(timeout=4)
        if self.__distT.is_alive():
            self.__outQ.put(item=None)
            self.__distT.join(timeout=4)
        return self

    def get_logger(self):
        return self.debug_logger

    def debug_on(self, **kwargs):
        """
        The debug_on function enables debug logging for the class.
        It accepts a number of optional keyword arguments:
            file_name - The name of the log file to write to, defaults to '<class_name>.log' if not specified.
            level - The minimum level at which this function will record data, defaults to DEBUG if not specified.
            show_level - A boolean indicating whether or not the log records should include the level of the message
            show_thread -
            show_module -
            show_method -
            date_filename -
            console_output -

        :param **kwargs: Used to Pass a variable number of arguments to the function.
        :return: None.

        :doc-author: Trelent
        """
        if self.debug_logger is None:
            self.debug_logger = LoggerWrapper(name=kwargs.get("file_name", self.name),
                                              level=kwargs.get("level", None),
                                              show_level=kwargs.get("show_level", True),
                                              show_thread=kwargs.get("show_thread", True),
                                              show_module=kwargs.get("show_module", True),
                                              show_method=kwargs.get("show_method", True),
                                              date_filename = kwargs.get("date_filename", True),
                                              console_output = kwargs.get("console_output", True))

        self.debug_write(topic="DEBUG", data="ON")
        self.subscribe(name="debug", call_back=self.__dbg_callback__, event=self.RX_EVENT)
        self.subscribe(name="debug", call_back=self.__dbg_callback__, event=self.TX_EVENT)

    def debug_off(self):
        """
        The debug_off function is used to turn off the debug logging.
        It is called by the user when they want to stop debugging and close their log file.

        :param self: Used to Access the class attributes and methods.
        :return: None.

        :doc-author: Trelent
        """
        if self.debug_logger is not None:
            self.debug_write(topic="DEBUG", data="OFF")
            self.unsubscribe(name="debug", event=self.RX_EVENT)
            self.unsubscribe(name="debug", event=self.TX_EVENT)
        self.debug_logger = None
        return self

    def debug_write(self, topic, data):
        """
        The debug_write function is a debugging tool. It is not intended to be used
        in production. debug_write will print the topic and data to a file or the console if
        debugging is enabled.  It's enabled by default.

        :param self: Used to Access the attributes and methods of the class in which it is used.
        :param topic: Used to Specify the name of the topic that is being published.
        :param data: Used to Pass the data to be written to the debug_logger.
        :return: The data that is passed into the function.

        :doc-author: Trelent
        """
        if self.debug_logger is not None:
            entry = "%s,%s" % (topic, data)
            self.debug_logger.info(entry)

    def __dbg_callback__(self, msg):
        """
        The __dbg_callback__ function is a callback function that is registered when the debugging is subscribed to
        the receive and transmit events, and called if the debug logger is enabled.  It will print out any messages
        received from the debugger to stdout and to a file.

        :param msg: Used to Pass the message to the debug logger.
        :return: The payload of the message.

        :doc-author: Trelent
        """
        if self.debug_logger is not None and msg is not None and msg['payload'] is not None:
            payload = msg['payload']
            if isinstance(payload, bytes):
                payload = payload.decode('ascii')
            if '\r\n' in payload:
                payload = payload.replace('\r\n', '')
            elif '\n' in payload:
                payload = payload.replace('\n', '')
            self.debug_write(topic=msg['event'], data=payload)

    def __process_input__(self, queue: Q):
        """
        The __process_input__ function is a private function that is registered as a thread callback function by the
        __run_thread__ function. It receives data from the socket and puts it into a queue to be processed.

        :param queue:Q: injected queue object to use for inter-thread communication
        :return: The data received from the socket.

        :doc-author: Trelent
        """
        while self.continue_thread:
            data = self._recv()
            if data is not None and len(data) > 0:
                queue.put(item=data)

    def __process_output__(self, queue: Q):
        """
        The __process_output__ function is a helper function that is used to send data from the output queue
        to the client. It does this by checking if there is any data in the queue, and if so it sends it to
        the client.  And posts a transmission event.

        :param queue:Q: injected queue object that holds the data
        :return: The data from the queue.

        :doc-author: Trelent
        """
        while self.continue_thread:
            data = queue.get(timeout=5)
            if data is not None:
                self._send(data=data)
                self.__event[self.TX_EVENT](payload=data)

    def __distribute_input__(self):
        """
        The __distribute_input__ function is a helper function that is called by the __input_thread__.
        It takes in data from the input queue and distributes it to the receive event subscribers.

        :return: A list of data from the input queue.

        :doc-author: Trelent
        """
        while self.continue_thread:
            data = self.__inQ.get(timeout=5)
            if data is not None:
                self.__event[self.RX_EVENT](payload=data)
