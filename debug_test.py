#!/usr/bin/env python3

import sys
sys.path.append('/home/jack/Documents/cpw')

from unittest.mock import MagicMock, patch
from pages.bitcoin_education import render_why_bitcoin_page

# Test to isolate the regex issue
try:
    # Mock streamlit entirely
    with patch.dict('sys.modules', {'streamlit': MagicMock()}):
        import streamlit as st
        st.header = MagicMock()
        st.info = MagicMock()
        st.markdown = MagicMock()
        st.write = MagicMock()
        st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
        st.subheader = MagicMock()
        st.metric = MagicMock()
        st.divider = MagicMock()
        st.caption = MagicMock()
        
        # Mock session state
        st.session_state = {}
        
        # Mock context and headers
        st.context = MagicMock()
        st.context.headers = MagicMock()
        st.context.headers.get = MagicMock(return_value="Test Browser")
        
        # Mock the debug logger separately
        with patch('pages.bitcoin_education.debug_log_user_action') as mock_logger:
            mock_logger.return_value = None
            
            print("About to call render_why_bitcoin_page")
            render_why_bitcoin_page()
            print("render_why_bitcoin_page completed successfully")
            
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()
