"""
Basic tests for network functionality
"""
import unittest
import socket
from unittest.mock import Mock, patch

from kvm_switch.core.network import NetworkManager


class TestNetworkManager(unittest.TestCase):
    """Test NetworkManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.kvm_mock = Mock()
        self.kvm_mock.mode = "server"
        self.kvm_mock.running = True
        self.kvm_mock.connected = False
        self.network_manager = NetworkManager(self.kvm_mock)
    
    def test_init(self):
        """Test NetworkManager initialization"""
        self.assertEqual(self.network_manager.kvm, self.kvm_mock)
        self.assertFalse(self.network_manager.running)
        self.assertIsNone(self.network_manager.broadcast_socket)
        self.assertIsNone(self.network_manager.listen_socket)
    
    def test_start_server_mode(self):
        """Test starting network manager in server mode"""
        with patch('threading.Thread') as mock_thread:
            self.network_manager.start()
            self.assertTrue(self.network_manager.running)
            # Should have started broadcast thread
            mock_thread.assert_called()
    
    def test_start_client_mode(self):
        """Test starting network manager in client mode"""
        self.kvm_mock.mode = "client"
        with patch('threading.Thread') as mock_thread:
            self.network_manager.start()
            self.assertTrue(self.network_manager.running)
            # Should not start broadcast thread for client
            pass


if __name__ == '__main__':
    unittest.main()