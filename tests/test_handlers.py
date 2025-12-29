"""
Test cases for handler functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json

from kvm_switch.handlers.input_handler import InputHandler
from kvm_switch.handlers.message_handler import MessageHandler

class TestInputHandler(unittest.TestCase):
    """Test cases for InputHandler class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.send_callback = Mock()
        self.server_handler = InputHandler('server', self.send_callback)
        self.client_handler = InputHandler('client', self.send_callback)
    
    def test_initialization(self):
        """Test InputHandler initialization"""
        self.assertEqual(self.server_handler.mode, 'server')
        self.assertEqual(self.client_handler.mode, 'client')
        self.assertFalse(self.server_handler.connected)
        self.assertFalse(self.client_handler.connected)
    
    def test_set_state(self):
        """Test state setting"""
        self.server_handler.set_state(True, True)
        self.assertTrue(self.server_handler.connected)
        self.assertTrue(self.server_handler.has_control)
    
    def test_screen_dimensions(self):
        """Test screen dimension setting"""
        self.server_handler.set_screen_dimensions(1920, 1080, 2560, 1440)
        self.assertEqual(self.server_handler.screen_width, 1920)
        self.assertEqual(self.server_handler.screen_height, 1080)
        self.assertEqual(self.server_handler.peer_screen_width, 2560)
        self.assertEqual(self.server_handler.peer_screen_height, 1440)

class TestMessageHandler(unittest.TestCase):
    """Test cases for MessageHandler class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.input_handler = Mock()
        self.control_callback = Mock()
        self.show_overlay = Mock()
        self.hide_overlay = Mock()
        
        self.server_handler = MessageHandler(
            'server', self.input_handler, 
            self.control_callback, self.show_overlay, self.hide_overlay
        )
        self.client_handler = MessageHandler(
            'client', self.input_handler,
            self.control_callback, self.show_overlay, self.hide_overlay
        )
    
    def test_initialization(self):
        """Test MessageHandler initialization"""
        self.assertEqual(self.server_handler.mode, 'server')
        self.assertEqual(self.client_handler.mode, 'client')
        self.assertFalse(self.server_handler.has_control)
        self.assertFalse(self.client_handler.has_control)
    
    def test_control_request_processing(self):
        """Test control request message processing"""
        control_msg = json.dumps({'type': 'control_request'}).encode()
        
        # Test client receiving control request
        self.client_handler.process_message(control_msg)
        self.assertTrue(self.client_handler.has_control)
        self.control_callback.assert_called_with(True)
        
        # Test server receiving control request
        self.server_handler.process_message(control_msg)
        self.assertFalse(self.server_handler.has_control)
        self.show_overlay.assert_called_once()
    
    def test_control_release_processing(self):
        """Test control release message processing"""
        release_msg = json.dumps({'type': 'control_release'}).encode()
        
        # Test server receiving control release
        self.server_handler.process_message(release_msg)
        self.assertTrue(self.server_handler.has_control)
        self.hide_overlay.assert_called_once()
        
        # Test client receiving control release
        self.client_handler.process_message(release_msg)
        self.assertFalse(self.client_handler.has_control)
    
    def test_invalid_message_handling(self):
        """Test handling of invalid messages"""
        invalid_msg = b"invalid json data"
        
        # Should not raise exception
        try:
            self.server_handler.process_message(invalid_msg)
            self.client_handler.process_message(invalid_msg)
        except Exception as e:
            self.fail(f"Invalid message handling raised exception: {e}")

if __name__ == '__main__':
    unittest.main()