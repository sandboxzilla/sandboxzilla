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

        Constructor

        param kwargs: most of the parameters are used to configure the logging framework

        """
        super(IPHelper, self).__init__(address="Address not defined",
                                       recv_proc=self.__process_input__,
                                       **kwargs)

    def __process_input__(self, queue: Q):
        """
        Collect incoming data into a message buffer before putting the buffer into an event queue
        :param queue:
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
        data = str(data)
        if data is not None and ('\r\n' not in data and '\n' not in data):
            data += '\r\n'
        data = data.encode('ascii')
        self._socket.sendall(data)

    def _recv(self, size=1024):
        return self._socket.recv(2)

    def _open(self, **kwargs):
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
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

    def beacon(self,
               frequency: float = 3.0,
               payload: str = '<ping>'):
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
