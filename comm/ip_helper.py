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
from __future__ import absolute_import

__author__ = 'Erol Yesin'

import socket
import sys
import time

from utils import Queue as Q
from .base_dev_helper import BaseCommDeviceHelper


class IPHelper(BaseCommDeviceHelper):

    def __init__(self, **kwargs):
        """
        The __init__ function is called when an instance of the class is created.
        It initializes all of the variables that are defined in it and makes them
        available for use throughout the life of the object.  In this case, we're using
        it to initialize a socket so that we can connect to a remote host.

        :param self: Used to Reference the object of the class.
        :param **kwargs: Used to Pass a keyworded, variable-length argument list.
        :return: The object of the class that is calling it.

        :doc-author: Trelent
        """
        super(IPHelper, self).__init__(address="Address not defined",
                                       recv_proc=self.__process_input__,
                                       **kwargs)

    def __process_input__(self, queue: Q):
        """
        The __process_input__ function is a private function that is called by the __run__ method.
        It collects incoming data into a message buffer before putting the buffer into an event queue.

        :param self: Used to Reference the object itself.
        :param queue:Q: Used to Pass the event queue to the __process_input__ function.
        :return: A string that contains the message buffer.

        :doc-author: Trelent
        """
        msg = ''
        while self.continue_thread:
            data = self._recv(size=2)
            if data is not None and len(data) > 0:
                msg += data.decode('ascii')
                if "\r\n" in msg or "\n" in msg:
                    queue.put(item=msg)
                    msg = ''
                continue

    def _send(self, data):
        """
        The _send function is a helper function that sends data to the server.
        It is used by the send_command function, but can also be used directly if you want to send raw data.

        :param self: Used to Reference the object itself.
        :param data: Used to Pass the data to be sent.
        :return: The data with a newline character appended to it.

        :doc-author: Trelent
        """
        data = str(data)
        if data is not None and ('\r\n' not in data and '\n' not in data):
            data += '\r\n'
        data = data.encode('ascii')
        self._socket.sendall(data)

    def _recv(self, size=1024):
        """
        The _recv function receives a message from the client and returns it.

        :param self: Used to Reference the class instance.
        :param size=1024: Used to Specify the maximum amount of data to be received at once.
        :return: The data received from the socket.

        :doc-author: Trelent
        """
        return self._socket.recv(2)

    def _open(self, **kwargs):
        """
        The _open function connects to the server at the address and port
        specified in kwargs.  If no address or port is specified, it will use
        the defaults of 127.0.0.2:2000

        :param self: Used to Reference the class instance.
        :param **kwargs: Used to Pass a keyworded, variable-length argument list.
        :return: The socket object.

        :doc-author: Trelent
        """
        try:
            address = kwargs.get("address", "127.0.0.1:2000")
            self.address = address.split(':')[0]
            self.port = int(address.split(':')[1])

            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.address, self.port))
        except socket.error as msg:
            print('Socket could not be created. Error Code : ' + str(msg))
            sys.exit()

    def _close(self):
        """
        The _close function closes the socket connection to the server.

        :param self: Used to Refer to the object itself.
        :return: The socket.

        :doc-author: Trelent
        """
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

    def beacon(self,
               frequency: float = 3.0,
               payload: str = '<ping>'):
        """
        The beacon function sends out a message at the specified frequency.
        The default frequency is 3Hz, or 3/second. The payload is
        the ascii message to transmit.

        :param self: Used to Access the class attributes.
        :param frequency:float=3.0: Used to Define the frequency of the beacon.
        :param payload:str='<ping>': Used to Define the message that is sent out.
        :return: A thread that can be started, stopped and joined.

        :doc-author: Trelent
        """
        """
        Test tool
        Send out an ascii message at defined frequency
        :param frequency: 1/(duration of sleep in seconds)
        :param payload: The ascii message to transmit
        """
        while self.continue_thread:
            self.send(payload)
            time.sleep(1.0/frequency)


if __name__ == "__main__":

    comm_obj = IPHelper(file_name='ip', date_filename=False)

    def on_in(pkt):
        data = pkt['payload']
        if data is not None and len(data) > 0:
            comm_obj.debug_write(topic='Received',
                                 data=data.replace('\n', '').replace('\r', ''))

    comm_obj.open(address='127.0.0.1:2000').start(name='ipHelper_utest', call_back=on_in)
    try:
        comm_obj.beacon(frequency=0.3)
    except KeyboardInterrupt:
        print('\nRemember me fondly!')
    finally:
        comm_obj.close()
