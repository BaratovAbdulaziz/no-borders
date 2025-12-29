"""
Test cases for network functionality
"""

import unittest
from unittest.mock import Mock, patch
import socket
import json

from kvm_switch.core.network import NetworkManager
from kvm_switch.utils.config import MAGIC_MESSAGE

class TestNetworkManager(unittest.TestCase):
    """Test cases for NetworkManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.callback_mock = Mock()
        self.server_manager = NetworkManager('server', self.callback_mock)
        self.client_manager = NetworkManager('client', self.callback_mock)
    
    def test_initialization(self):
        """Test NetworkManager initialization"""
        self.assertEqual(self.server_manager.mode, 'server')
        self.assertEqual(self.client_manager.mode, 'client')
        self.assertFalse(self.server_manager.connected)
        self.assertFalse(self.client_manager.connected)
    
    def test_send_message(self):
        """Test sending messages"""
        # Mock socket
        mock_sock = Mock()
        self.server_manager.sock = mock_sock
        self.server_manager.connected = True
        
        test_message = {'type': 'test', 'data': 'hello'}
        result = self.server_manager.send_message(test_message)
        
        self.assertTrue(result)
        mock_sock.sendall.assert_called_once()
        
        # Verify the message was JSON encoded
        sent_data = mock_sock.sendall.call_args[0][0]
        self.assertIn(b'"type": "test"', sent_data)
    
    def test_disconnect(self):
        """Test disconnection cleanup"""
        mock_sock = Mock()
        self.server_manager.sock = mock_sock
        self.server_manager.connected = True
        
        self.server_manager.disconnect()
        
        self.assertFalse(self.server_manager.running)
        self.assertFalse(self.server_manager.connected)
        self.assertIsNone(self.server_manager.sock)
        mock_sock.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()