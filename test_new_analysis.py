#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the new analysis functionality
"""

import os
import subprocess

def test_new_analysis():
    """Test launching analysis with environment variables"""
    
    # Set test URL
    test_url = "https://example.com"
    
    # Prepare environment
    env = os.environ.copy()
    env['ANALYSIS_URL'] = test_url
    env['ENABLE_LLM_ANALYSIS'] = 'false'  # Disable for quick test
    env['ENABLE_ENHANCED_ANALYSIS'] = 'false'  # Disable for quick test
    
    print(f"🧪 Testing analysis for: {test_url}")
    print("⚠️ LLM and Enhanced analysis disabled for testing")
    
    try:
        # Launch analysis
        cmd = ["uv", "run", "python", "-m", "src.page_analyzer"]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,  # 1 minute timeout for test
            env=env
        )
        
        if process.returncode == 0:
            print("✅ Test passed!")
            print("📄 STDOUT:")
            print(process.stdout)
        else:
            print("❌ Test failed!")
            print(f"Return code: {process.returncode}")
            print("📄 STDERR:")
            print(process.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏱️ Test timed out")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_new_analysis()