# -*- coding: utf-8 -*-
"""
Used to decode the Victron Energy VE.Direct text protocol.

This is a forked version of script originally created by Janne Kario.
(https://github.com/karioja/vedirect).
 .. raises:: InputReadException,
             serial.SerialException,
             serial.SerialTimeoutException
"""
import logging
import time
from vedirect_m8.serconnect import SerialConnection
from vedirect_m8.exceptions import SettingInvalidException, InputReadException, TimeoutException, VedirectException

__author__ = "Janne Kario, Eli Serra"
__copyright__ = "Copyright 2015, Janne Kario"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class Vedirect:
    """
    Used to decode the Victron Energy VE.Direct text protocol.

    This is a forked version of script originally created by Janne Kario.
    (https://github.com/karioja/vedirect).

    .. raises:: InputReadException,
                 serial.SerialException,
                 serial.SerialTimeoutException
    """
    def __init__(self,
                 serial_port: str or None = None,
                 baud: int = 19200,
                 timeout: int or float = 0,
                 source_name: str = 'Vedirect'
                 ):
        """
        Constructor of Vedirect class.

        :Example:
            - > sc = Vedirect(serial_port = "/dev/ttyUSB1")
            - > sc.connect()
            - > True # if connection opened on serial port "/dev/tyyUSB1"
        :param self: Refer to the object instance itself,
        :param serial_port: The serial port to connect,
        :param baud: Baud rate such as 9600 or 115200 etc.
        :param timeout: Set a read timeout value in seconds,
        :param source_name: This is used in logger to identify the source of call.
        :return: Nothing
        """
        self._com = None
        self.header1 = ord('\r')
        self.header2 = ord('\n')
        self.hexmarker = ord(':')
        self.delimiter = ord('\t')
        self.key = ''
        self.value = ''
        self.bytes_sum = 0
        self.state = self.WAIT_HEADER
        self.dict = {}
        self.init_settings(serial_port=serial_port,
                           baud=baud,
                           timeout=timeout,
                           source_name=source_name
                           )

    (HEX, WAIT_HEADER, IN_KEY, IN_VALUE, IN_CHECKSUM) = range(5)

    @staticmethod
    def is_serial_com(obj: SerialConnection) -> bool:
        """
        Test if obj is valid SerialConnection instance.

        :Example :
            - >Vedirect.is_serial_com(obj=my_object)
            - >True
        :param obj: The object to test.
        :return: True if obj is valid SerialConnection instance.
        """
        return isinstance(obj, SerialConnection)

    @staticmethod
    def is_timeout(elapsed: float or int, timeout: float or int = 60) -> bool:
        """
        Test if elapsed time is greater than timeout.

        :Example :
            - >Vedirect.is_timeout(elapsed=45, timeout=60)
            - >True
        :param elapsed: The elapsed time to test,
        :param timeout: The timeout to evaluate.
        :return: True if elapsed time is upper than timeout.
        """
        if elapsed >= timeout:
            raise TimeoutException(
                '[VeDirect::is_timeout] '
                'Unable to read serial data. '
                'Timeout error.'
            )
        return True

    def has_serial_com(self) -> bool:
        """Test if self._com is a valid SerialConnection instance."""
        return Vedirect.is_serial_com(self._com)

    def is_serial_ready(self) -> bool:
        """Test if is serial connection is ready"""
        return self.has_serial_com() and self._com.is_ready()

    def is_ready(self) -> bool:
        """Test if class Vedirect is ready"""
        return self.is_serial_ready()

    def connect_to_serial(self) -> bool:
        """ Connect to serial port if not connected """
        if self.has_serial_com():
            if (not self._com.is_ready() and self._com.connect()) or self._com.is_ready():
                return True
        return False

    def init_serial_connection_from_object(self, serial_connection: SerialConnection) -> bool:
        """
        Initialise serial connection from SerialConnection object
        Raise:
         - SettingInvalidException if serial_port, baud or timeout are not valid.
         - VedirectException if connection to serial port fails
        :Example :
            - >self.init_serial_connection(serial_port="/tmp/vmodem0")
            - >True
        :param self: Refer to the object itself,
        :param serial_connection: The SerialConnection object,
        :return: True if connection to serial port success.
        .. raises:: SettingInvalidException, VedirectException
        """
        if Vedirect.is_serial_com(serial_connection) and serial_connection.is_settings():
            self._com = serial_connection
            if not self.connect_to_serial():
                raise VedirectException(
                    "[Vedirect::init_serial_connection_from_object] "
                    "Connection to serial port fails. obj : %s" %
                    serial_connection
                )
            return True
        else:
            raise SettingInvalidException(
                "[Vedirect::init_serial_connection_from_object] "
                "Unable to init init_serial_connection_from_object, "
                "bad parameters : %s" %
                serial_connection
            )

    def init_serial_connection(self,
                               serial_port: str or None = None,
                               baud: int = 19200,
                               timeout: int or float = 0,
                               source_name: str = 'Vedirect'
                               ) -> bool:
        """
        Initialise serial connection from parameters.

        At least serial_port must be provided.
        Default :
         - baud rate = 19200,
         - timeout = 0 (non blocking mode)
         - source_name = 'Vedirect'
        Raise:
         - SettingInvalidException if serial_port, baud or timeout are not valid.
         - VedirectException if connection to serial port fails
        :Example :
            - >self.init_serial_connection(serial_port="/tmp/vmodem0")
            - >True
        :param self: Refer to the object itself,
        :param serial_port: The serial port to connect,
        :param baud: Baud rate such as 9600 or 115200 etc.
        :param timeout: Set a read timeout value in seconds,
        :param source_name: This is used in logger to identify the source of call.
        :return: True if connection to serial port success.
        .. raises:: SettingInvalidException, VedirectException
        """
        if SerialConnection.is_serial_conf(serial_port=serial_port,
                                           baud=baud,
                                           timeout=timeout
                                           ):
            self._com = SerialConnection(serial_port=serial_port,
                                         baud=baud,
                                         timeout=timeout,
                                         source_name=source_name
                                         )
            if not self.connect_to_serial():
                raise VedirectException(
                    "[Vedirect::init_serial_connection] "
                    "Connection to serial port %s fails." %
                    serial_port
                )
            return True
        else:
            raise SettingInvalidException(
                "[Vedirect::init_serial_connection] "
                "Unable to init SerialConnection, "
                "bad parameters. serial_port : %s - baud : %s - timeout : %s." %
                (serial_port, baud, timeout)
            )

    def init_settings(self,
                      serial_port: str or None = None,
                      baud: int = 19200,
                      timeout: int or float = 0,
                      source_name: str = 'Vedirect'
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
        :param self: Refer to the object itself,
        :param serial_port: The serial port to connect,
        :param baud: Baud rate such as 9600 or 115200 etc.
        :param timeout: Set a read timeout value in seconds,
        :param source_name: This is used in logger to identify the source of call.
        :return: True if connection to serial port success.
        .. raises:: SettingInvalidException, VedirectException
        """
        return self.init_serial_connection(serial_port=serial_port,
                                           baud=baud,
                                           timeout=timeout,
                                           source_name=source_name)

    def init_data_read(self):
        """ Initialise reader properties """
        self.key = ''
        self.value = ''
        self.bytes_sum = 0
        self.state = self.WAIT_HEADER
        self.dict = {}

    def input_read(self, byte) -> dict or None:
        """Input read from byte."""
        try:
            nbyte = ord(byte)
            if byte == self.hexmarker and self.state != self.IN_CHECKSUM:
                self.state = self.HEX
            if self.state == self.WAIT_HEADER:
                self.bytes_sum += nbyte
                if nbyte == self.header1:
                    self.state = self.WAIT_HEADER
                elif nbyte == self.header2:
                    self.state = self.IN_KEY
                return None
            elif self.state == self.IN_KEY:
                self.bytes_sum += nbyte
                if nbyte == self.delimiter:
                    if self.key == 'Checksum':
                        self.state = self.IN_CHECKSUM
                    else:
                        self.state = self.IN_VALUE
                else:
                    self.key += byte.decode('ascii')
                return None
            elif self.state == self.IN_VALUE:
                self.bytes_sum += nbyte
                if nbyte == self.header1:
                    self.state = self.WAIT_HEADER
                    self.dict[self.key] = self.value
                    self.key = ''
                    self.value = ''
                else:
                    self.value += byte.decode('ascii')
                return None
            elif self.state == self.IN_CHECKSUM:
                self.bytes_sum += nbyte
                self.key = ''
                self.value = ''
                self.state = self.WAIT_HEADER
                if self.bytes_sum % 256 == 0:
                    self.bytes_sum = 0
                    return self.dict
                else:
                    self.bytes_sum = 0
            elif self.state == self.HEX:
                self.bytes_sum = 0
                if nbyte == self.header2:
                    self.state = self.WAIT_HEADER
            else:
                raise AssertionError()
        except Exception as ex:
            raise InputReadException(
                "[Vedirect::input_read] "
                "Serial input read error %s " % ex
            )

    def get_serial_packet(self) -> dict or None:
        """
        Return Ve Direct block packet from serial reader.

        Read a byte from serial and decode him with vedirect protocol.
        :return: A dictionary of vedirect block data or None if block not entirely decoded.
        """
        byte = self._com.ser.read(1)
        if byte == b'\x00':
            byte = self._com.ser.read(1)
        return self.input_read(byte)

    def read_data_single(self, timeout: int = 60) -> dict or None:
        """
        Read a single block decoded from serial port and returns it as a dictionary.

        :Example :
            - > ve = Vedirect(serial_port="/tmp/vemodem1")
            - > ve.read_data_single(timeout=3)
            - > {'V': '12800', 'VS': '12800', 'VM': '1280', ...}

        :param self: Reference the class instance
        :param timeout: Set the timeout for the read_data_single function
        :return: A dictionary of the data
        :doc-author: Trelent
        """
        bc, now, tim = True, time.time(), 0

        if self.is_ready():
            while bc:
                packet, tim = None, time.time()

                packet = self.get_serial_packet()

                if packet is not None:
                    logger.debug("Serial reader success: dict: %s" % self.dict)
                    return packet

                # timeout serial read
                Vedirect.is_timeout(tim-now, timeout)
        else:
            logger.error('[VeDirect] Unable to read serial data. Not connected to serial port...')

        return None

    def read_data_callback(self,
                           callback_function,
                           timeout: int = 60,
                           max_loops: int or None = None
                           ):
        """
        Read data from the serial port and returns it to a callback function.

        :param self: Reference the class instance
        :param callback_function:function: Pass a function to the read_data_callback function
        :param timeout:int=60: Set the timeout for the read_data_callback function
        :param max_loops:int or None=None: Limit the number of loops
        """
        bc, now, tim, i = True, time.time(), 0, 0
        packet = None
        if self.is_ready():
            while bc:
                tim = time.time()

                packet = self.get_serial_packet()

                if packet is not None:
                    logger.debug(
                        "Serial reader success: packet: %s "
                        "-- state: %s -- bytes_sum: %s " %
                        (packet, self.state, self.bytes_sum))
                    callback_function(packet)
                    now = tim
                    i = i + 1
                    packet = None

                # timeout serial read
                Vedirect.is_timeout(tim-now, timeout)
                if isinstance(max_loops, int) and 0 < max_loops <= i:
                    return True
                time.sleep(0.1)
        else:
            raise VedirectException(
                '[VeDirect::read_data_callback] '
                'Unable to read serial data. '
                'Not connected to serial port...')
