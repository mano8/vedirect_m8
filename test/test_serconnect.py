# -*- coding: utf-8 -*-
"""
SerialConnection unittest class.

Use pytest package.
"""
import os
from vedirect_m8.serconnect import SerialConnection
from vedirect_m8.serutils import SerialUtils as Ut

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"


class TestSerialConnection:

    def setup_method(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """
        conf = {
            'serial_port': "/tmp/vmodem1",
            'baud': 19200,
            'timeout': 0,
        }

        if not SerialConnection.is_serial_port_exists("/tmp/vmodem1"):
            conf.update(
                {'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem1")}
            )
        self.obj = SerialConnection(**conf)

    def teardown_method(self):
        """ teardown any state that was previously setup with a setup_function
        call.
        """
        pass

    def test_settings(self):
        """Test configuration settings from SerialConnection constructor"""
        assert self.obj.is_settings()

    def test_set_timeout(self):
        """Test set_timeout method"""
        assert self.obj.set_timeout(0)
        assert self.obj.set_timeout(10)
        assert not self.obj.set_timeout(-1)
        assert not self.obj.set_timeout("hello")

    def test_set_source_name(self):
        """Test set_source_name method"""
        assert self.obj.set_source_name("hello")
        assert not self.obj.set_source_name("")
        assert not self.obj.set_source_name(-1)
        assert not self.obj.set_source_name(None)

    def test_get_virtual_ports_paths(self):
        """Test get_virtual_ports_paths method"""
        paths = SerialConnection.get_virtual_ports_paths()
        assert Ut.is_list(paths) and len(paths) == 2
        assert paths[0] == "/tmp"
        assert paths[1] == os.path.expanduser('~')

    def test_get_virtual_home_serial_port(self):
        """Test get_virtual_home_serial_port method"""
        v_ports = [
            SerialConnection.get_virtual_home_serial_port("vmodem999"),
            SerialConnection.get_virtual_home_serial_port("vmodem0"),
            SerialConnection.get_virtual_home_serial_port("vmodem"),
            SerialConnection.get_virtual_home_serial_port("vmodem9999"),
            SerialConnection.get_virtual_home_serial_port("z9999"),
            SerialConnection.get_virtual_home_serial_port(1),
            SerialConnection.get_virtual_home_serial_port(dict())
        ]
        tests = [x for x in v_ports if x is not None]
        assert len(tests) == 2

    def test_is_virtual_serial_port(self):
        """Test is_virtual_serial_port method"""
        v_ports = [
            SerialConnection.get_virtual_home_serial_port("vmodem999"),
            SerialConnection.get_virtual_home_serial_port("vmodem0"),
            SerialConnection.get_virtual_home_serial_port("vmodem"),
            SerialConnection.get_virtual_home_serial_port("vmodem9999"),
            SerialConnection.get_virtual_home_serial_port("z9999"),
            SerialConnection.get_virtual_home_serial_port(1),
            SerialConnection.get_virtual_home_serial_port(dict())
        ]
        tests = [x for x in v_ports if SerialConnection.is_virtual_serial_port(x)]
        assert len(tests) == 2

    def test_split_serial_port(self):
        """Test split_serial_port method"""
        ports = [
            "r",
            "/r",
            "a/b/c/r",
            "/r/",
            "\\r"
        ]
        tests = [x for x in ports if SerialConnection.split_serial_port(x)[0] == 'r']
        assert len(tests) == 3

    def test_is_serial_port_exists(self):
        """Test is_serial_port_exists method"""
        ports = [
            "/tmp/vmodem0",
            "/tmp/vmodem1",
            SerialConnection.get_virtual_home_serial_port("vmodem0"),
            SerialConnection.get_virtual_home_serial_port("vmodem1")
        ]
        tests = [x for x in ports if SerialConnection.is_serial_port_exists(x)]
        assert len(tests) == 2

    def test_is_serial_port(self):
        """Test is_serial_port method"""
        ports = [
            "/tmp/vmodem0",
            "/tmp/vmodem1",
            SerialConnection.get_virtual_home_serial_port("vmodem0"),
            SerialConnection.get_virtual_home_serial_port("vmodem1"),
            "/dev/ttyUSB1",
            "/dev/ttyACM1",
            "/dev/vmodem0",
            "/dev/vmodem1",
            "/dev/COM1",
            "COM1",
            "COM1999",  # false
            "/dev/USB1",  # false
            "/dev/ACM1",  # false
            "/dev/1",  # false
        ]
        tests = [x for x in ports if SerialConnection.is_serial_port(x)]
        assert len(tests) == 10

    def test_is_serial_path(self):
        """Test is_serial_path method"""
        paths = [
            "/tmp",  # true
            os.path.expanduser('~'),  # true
            "/dev",  # true
            "/dev/pts/",
            "/var",
            "/var/run/",
            1,
            1.1,
            ("COM1999", 1),
            dict(),
            None
        ]
        tests = [x for x in paths if SerialConnection.is_serial_path(x)]
        assert len(tests) == 3

    def test_is_baud(self):
        """Test is_baud method"""
        bauds = [
            110, 300, 600, 1200,
            2400, 4800, 9600, 14400,
            19200, 38400, 57600, 115200,
            128000, 256000, 0, 1, 10, 302,
            2500, 4900, "300"
        ]
        tests = [x for x in bauds if SerialConnection.is_baud(x)]
        assert len(tests) == 14

    def test_is_timeout(self):
        """Test is_timeout method"""
        timeouts = [
            1, 5, 10, 0.1, 0, None,
            "2400"
        ]
        tests = [x for x in timeouts if SerialConnection.is_timeout(x)]
        assert len(tests) == 6

    def test_set_serial_conf(self):
        """Test set_serial_conf method"""
        conf = {
            'serial_port': "/tmp/vmodem0",
            'baud': 19200,
            'timeout': 0,
            'write_timeout': 0,
            'exclusive': True
        }
        result = self.obj.set_serial_conf(**conf)
        assert Ut.is_dict(result, eq=5)

    def test_connect(self):
        """Test connect method"""
        assert self.obj.connect()
        assert self.obj.is_serial_ready()
        assert self.obj.is_ready()
        
    def test_get_serial_ports_list(self):
        """Test get_serial_ports_list method"""
        serial_ports = self.obj.get_serial_ports_list()
        assert Ut.is_list(serial_ports) and len(serial_ports) == 2

    def test_get_unix_virtual_serial_ports_list(self):
        """Test get_unix_virtual_serial_ports_list method"""
        serial_ports = self.obj.get_unix_virtual_serial_ports_list()
        assert Ut.is_list(serial_ports) and len(serial_ports) == 2
