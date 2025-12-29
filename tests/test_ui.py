"""
Test cases for UI functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk

from kvm_switch.ui.control_panel import ControlPanel, show_role_selection_dialog
from kvm_switch.ui.splash import SplashScreen
from kvm_switch.ui.overlay import ServerOverlay

class TestControlPanel(unittest.TestCase):
    """Test cases for ControlPanel class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.toggle_callback = Mock()
        self.cleanup_callback = Mock()
        self.control_panel = ControlPanel(
            self.toggle_callback, 
            self.cleanup_callback
        )
    
    def test_initialization(self):
        """Test ControlPanel initialization"""
        self.assertEqual(self.control_panel.toggle_callback, self.toggle_callback)
        self.assertEqual(self.control_panel.cleanup_callback, self.cleanup_callback)
        self.assertIsNone(self.control_panel.root)
        self.assertIsNone(self.control_panel.control_button)
    
    @patch('tkinter.Tk')
    def test_create_ui(self, mock_tk):
        """Test UI creation"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        self.control_panel.create()
        
        # Verify Tk was called
        mock_tk.assert_called_once()
        self.assertIsNotNone(self.control_panel.root)
    
    def test_update_state_disconnected(self):
        """Test UI state update when disconnected"""
        # Create mock button
        mock_button = Mock()
        self.control_panel.control_button = mock_button
        
        self.control_panel.update_state(False, False, 'server')
        
        mock_button.config.assert_called_with(
            bg='gray', 
            text='Disconnected', 
            state='disabled'
        )
    
    def test_update_state_has_control(self):
        """Test UI state update when has control"""
        mock_button = Mock()
        self.control_panel.control_button = mock_button
        
        self.control_panel.update_state(True, True, 'server')
        
        mock_button.config.assert_called_with(
            bg='green', 
            text='You Have Control', 
            state='normal'
        )
    
    def test_update_state_no_control_server(self):
        """Test UI state update when server has no control"""
        mock_button = Mock()
        self.control_panel.control_button = mock_button
        
        self.control_panel.update_state(True, False, 'server')
        
        mock_button.config.assert_called_with(
            bg='red', 
            text='No Control', 
            state='disabled'
        )
    
    def test_update_state_no_control_client(self):
        """Test UI state update when client has no control"""
        mock_button = Mock()
        self.control_panel.control_button = mock_button
        
        self.control_panel.update_state(True, False, 'client')
        
        mock_button.config.assert_called_with(
            bg='red', 
            text='No Control', 
            state='normal'
        )

class TestSplashScreen(unittest.TestCase):
    """Test cases for SplashScreen class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.splash_screen = SplashScreen()
    
    def test_initialization(self):
        """Test SplashScreen initialization"""
        self.assertIsNone(self.splash_screen.splash)
        self.assertIsNone(self.splash_screen.canvas)

class TestServerOverlay(unittest.TestCase):
    """Test cases for ServerOverlay class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parent_root = Mock()
        self.overlay = ServerOverlay(self.parent_root)
    
    def test_initialization(self):
        """Test ServerOverlay initialization"""
        self.assertIsNone(self.overlay.overlay)
        self.assertEqual(self.overlay.parent_root, self.parent_root)
        self.assertIsNone(self.overlay.canvas)
    
    def test_is_visible_initially(self):
        """Test overlay visibility check when not shown"""
        self.assertFalse(self.overlay.is_visible())
    
    def test_hide_when_not_visible(self):
        """Test hiding overlay when not visible"""
        # Should not raise exception
        try:
            self.overlay.hide()
        except Exception as e:
            self.fail(f"Hiding non-visible overlay raised exception: {e}")

if __name__ == '__main__':
    unittest.main()