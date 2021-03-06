#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Used to decode the Victron Energy VE.Direct text protocol.

Extends Vedirect, and add ability to wait for serial connection,
at start, and or when reading serial data.

 .. seealso:: Vedirect
 .. raises:: InputReadException,
             serial.SerialException,
             serial.SerialTimeoutException,
             VedirectException
"""
import logging
import time
import serial

from ve_utils.utype import UType as Ut
from vedirect_m8.sertest import SerialTestHelper
from vedirect_m8.vedirect import Vedirect
from vedirect_m8.serconnect import SerialConnection
from vedirect_m8.exceptions import InputReadException, TimeoutException, VedirectException, SettingInvalidException

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class VedirectController(Vedirect):
    """
    Used to decode the Victron Energy VE.Direct text protocol.

    Extends Vedirect, and add ability to wait for serial connection,
    at start, and or when reading serial data.

     .. seealso:: Vedirect
     .. raises:: InputReadException,
                 serial.SerialException,
                 serial.SerialTimeoutException,
                 VedirectException
    """
    def __init__(self,
                 serial_test: dict,
                 serial_port: str or None = None,
                 baud: int = 19200,
                 timeout: int or float = 0,
                 source_name: str = 'VedirectController',
                 ):
        """
        Constructor of VedirectController class.

        :Example:
            - > sc = VedirectController(serial_port = "/dev/ttyUSB1")
            - > sc.connect()
            - > True # if connection opened on serial port "/dev/tyyUSB1"
        :param self: Refer to the object instance itself,
        :param serial_test: The serial_test to execute to retrieve the serial port,
        :param serial_port: The serial port to connect,
        :param baud: Baud rate such as 9600 or 115200 etc.
        :param timeout: Set a read timeout value in seconds,
        :param source_name: This is used in logger to identify the source of call.
        :return: Nothing
        """
        Vedirect.__init__(self,
                          serial_port=serial_port,
                          baud=baud,
                          timeout=timeout,
                          source_name=source_name)
        self._ser_test = None
        self.init_serial_test(serial_test)

    def has_serial_test(self) -> bool:
        """Test if is valid serial test helper."""
        return isinstance(self._ser_test, SerialTestHelper)\
            and self._ser_test.has_serial_tests()

    def is_ready(self) -> bool:
        """Test if class Vedirect is ready."""
        return self.is_serial_ready() and self.has_serial_test()

    def is_ready_to_search_ports(self) -> bool:
        """Test if class Vedirect is ready."""
        return self.has_serial_com() and self.has_serial_test()

    def init_serial_test(self, serial_test: dict) -> bool:
        """
        Initialises the serial test helper.

        It takes a dictionary of arguments and passes it to SerialTestHelper,
        Raise SettingInvalidException
        :param self: Refer to the object of the class
        :param serial_test: The serial_test to execute to retrieve the serial port,
        :return: True if SerialTestHelper initialisation success.
        """
        if Ut.is_dict(serial_test, not_null=True):
            self._ser_test = SerialTestHelper(serial_test)
            if not self._ser_test.has_serial_tests():
                raise SettingInvalidException(
                    "[Vedirect::init_serial_test] "
                    "Unable to init SerialTestHelper, "
                    "bad parameters : %s." %
                    serial_test
                )
            return True
        raise SettingInvalidException(
            "[Vedirect::init_serial_test] "
            "Unable to init SerialTestHelper, "
            "bad parameters : %s." %
            serial_test
        )

    def init_settings(self,
                      serial_port: str or None = None,
                      baud: int = 19200,
                      timeout: int or float = 0,
                      source_name: str = 'VedirectController',
                      wait_timeout: int or float = 3600
                      ) -> bool:
        """
        Initialise the settings for the class.

        At least serial_port must be provided.
        Default :
         - baud rate = 19200,
         - timeout = 0 (non blocking mode)
         - source_name = 'Vedirect'
        Raise:
         - SettingInvalidException if serial_port, baud or timeout are not valid.
         - VedirectException if connection to serial port fails
        :Example :
            - >self.init_settings(serial_port="/tmp/vmodem0")
            - >True
        :param self: Refer to the object itself
        :param serial_port: The serial port to connect
        :param baud: Baud rate such as 9600 or 115200 etc.
        :param timeout: Set a read timeout value in seconds
        :param source_name: This is used in logger to identify the source of call
        :param wait_timeout: Timeout value to search valid serial port in case of connection fails
        :return: True if connection to serial port success.

        .. raises:: SettingInvalidException, VedirectException
        """
        try:
            return self.init_serial_connection(serial_port=serial_port,
                                               baud=baud,
                                               timeout=timeout,
                                               source_name=source_name
                                               )
        except VedirectException as ex:
            if self.wait_or_search_serial_connection(timeout=wait_timeout, exception=ex):
                return True
        return False

    def read_data_to_test(self) -> dict:
        """Return decoded Vedirect blocks from serial to identify the right serial port."""
        res = None
        if self.is_ready():
            try:
                res = dict()
                data = self.read_data_single(timeout=1)
                if Ut.is_dict(data, not_null=True):
                    res.update(data)
            except Exception as ex:
                logger.debug(
                    '[VeDirect] Unable to read serial data to test'
                    'ex : %s' % ex
                )
        return res

    def test_serial_ports(self, ports: list) -> bool:
        """
        Test the serial connection to a VeDirect device.

        It takes in a list of ports and
        tests each port for the presence of a VeDirect device.
        If it finds one, it attempts to connect to that port
        and reads data from it. It then passes this data into
        the SerialTestHelper class which runs some basic tests
        on the data returned by the serial connection.
        :param self: Reference the class instance
        :param ports:list: Specify the serial ports to test
        :return: True if the serial port is open and
                 connected to a device that returns valid data

        .. raises:: VedirectException,
        :doc-author: Trelent
        """
        if self.is_ready_to_search_ports():
            if Ut.is_list(ports, not_null=True):
                for port in ports:
                    if SerialConnection.is_serial_port(port):

                        if self._com.connect(**{"serial_port": port, 'timeout': 0}):
                            time.sleep(0.5)
                            data = self.read_data_to_test()
                            if self._ser_test.run_serial_tests(data):
                                self._com.ser.timeout = self._com._timeout
                                logger.info(
                                    "[VeDirect::test_serial_ports] "
                                    "New connection established to serial port %s. " %
                                    port
                                )
                                return True
                            else:
                                self._com.ser.close()

                return False
        else:
            raise VedirectException(
                "[VeDirect::test_serial_ports] "
                "Unable to test to any serial port. "
                "SerialConnection and/or SerialTestHelper, "
                "are not ready."
            )

    def search_serial_port(self) -> bool:
        """Search the serial port from serial tests."""
        if self.is_ready_to_search_ports():
            ports = self._com.get_serial_ports_list()
            if self.test_serial_ports(ports):
                self.init_data_read()
                return True
        return False

    def wait_or_search_serial_connection(self,
                                         exception: Exception or None = None,
                                         timeout: int or float = 18400
                                         ) -> bool:
        """
        Wait or search for a new serial connection.

        It will first check if the VeDirect object has a SerialConnection,
        and SerialTestHelper with valid tests to run.
        If not, raise an VedirectException.
        Else if both of these are true, get a list of available serial ports,
        and call the test_serial_ports function on itself,
        to retrieve valid serial port, and connect to him.
        Return True or False depending on whether there is an active serial connection.
        Raise a TimeoutException in case there is no active serial connection,
        within the given timeout time
        :param self: Reference the class instance
        :param exception: Pass an exception to the function
        :param timeout: Set the timeout of the function
        :return: True if the serial connection was successful

        .. raises:: TimeoutException, VedirectException
        :doc-author: Trelent
        """
        if self.is_ready_to_search_ports():
            logger.info(
                "[VeDirect::wait_or_search_serial_connection] "
                "Lost serial connection, attempting to reconnect. "
                "reconnection timeout is set to %ss" % timeout
            )
            bc, now, tim = True, time.time(), 0
            while bc:
                tim = time.time()
                if self.search_serial_port():
                    return True

                if tim-now > timeout:
                    raise TimeoutException(
                        "[VeDirect::wait_or_search_serial_connection] "
                        "Unable to connect to any serial item. "
                        "Timeout error : %s. Exception : %s" %
                        (timeout, exception)
                    )

                time.sleep(2.5)
        raise VedirectException(
            "[VeDirect::wait_or_search_serial_connection] "
            "Unable to connect to any serial item. "
            "Exception : %s" % exception
        )

    def read_data_callback(self,
                           callback_func,
                           timeout: int = 60,
                           connection_timeout: int = 3600,
                           max_loops: int or None = None
                           ) -> dict or None:
        """
        Read data from the serial port and returns it to a callback function.

        :param self: Reference the class instance
        :param callback_func:function: Pass a function to the read_data_callback function
        :param timeout:int=60: Set the timeout for the read_data_callback function
        :param connection_timeout:int=18400: Set the timeout for the connection
        :param max_loops:int or None=None: Limit the number of loops
        :return: A dictionary
        :doc-author: Trelent
        """
        bc, now, tim, i = True, time.time(), 0, 0
        packet = None
        if self.is_ready():
            while bc:
                tim = time.time()
                try:
                    packet = self.get_serial_packet()
                except (
                        InputReadException,
                        serial.SerialException,
                        serial.SerialTimeoutException
                        ) as ex:
                    if self.wait_or_search_serial_connection(ex, connection_timeout):
                        now = tim = time.time()
                        packet = self.get_serial_packet()

                if packet is not None:
                    logger.debug(
                        "Serial reader success: "
                        "packet: %s -- "
                        "state: %s -- "
                        "bytes_sum: %s " %
                        (packet, self.state, self.bytes_sum)
                    )
                    callback_func(packet)
                    now = tim
                    i = i+1
                    packet = None

                # timeout serial read
                Vedirect.is_timeout(tim - now, timeout)

                if Ut.is_int(max_loops) and i >= max_loops:
                    return True
                time.sleep(0.1)
        else:
            logger.error(
                '[VeDirect::read_data_callback] '
                'Unable to read serial data. '
                'Not connected to serial port...')
        
        callback_func(None)
