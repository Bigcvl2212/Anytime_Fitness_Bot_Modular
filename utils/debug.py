"""
Debug Utilities
Tools for debugging, logging, and troubleshooting the Gym Bot application.
"""

import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
from selenium.webdriver.common.by import By

from ..config.constants import DEBUG_FOLDER

class DebugManager:
    """Manages debug operations and state capture."""
    
    def __init__(self, debug_folder: str = DEBUG_FOLDER):
        self.debug_folder = debug_folder
        self._ensure_debug_folder()
    
    def _ensure_debug_folder(self):
        """Ensure debug folder exists."""
        if not os.path.exists(self.debug_folder):
            os.makedirs(self.debug_folder)
            print(f"✅ Created debug folder: {self.debug_folder}")
    
    def capture_page_state(
        self, 
        driver, 
        debug_name: str,
        include_screenshot: bool = True,
        include_html: bool = True,
        include_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Capture comprehensive page state for debugging.
        
        Args:
            driver: WebDriver instance
            debug_name (str): Name for the debug session
            include_screenshot (bool): Whether to take a screenshot
            include_html (bool): Whether to save HTML source
            include_analysis (bool): Whether to analyze page elements
            
        Returns:
            Dict[str, Any]: Debug information and file paths
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_filename = f"debug_{debug_name}_{timestamp}"
            
            results = {
                'timestamp': timestamp,
                'debug_name': debug_name,
                'current_url': driver.current_url,
                'page_title': driver.title,
                'files_created': []
            }
            
            # Capture screenshot
            if include_screenshot:
                screenshot_path = os.path.join(self.debug_folder, f"{base_filename}_screenshot.png")
                driver.save_screenshot(screenshot_path)
                results['screenshot_path'] = screenshot_path
                results['files_created'].append(screenshot_path)
                print(f"   📸 Screenshot saved: {screenshot_path}")
            
            # Save HTML source
            if include_html:
                html_path = os.path.join(self.debug_folder, f"{base_filename}_source.html")
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                results['html_path'] = html_path
                results['files_created'].append(html_path)
                print(f"   📄 HTML source saved: {html_path}")
            
            # Analyze page elements
            if include_analysis:
                analysis = self._analyze_page_elements(driver)
                results['element_analysis'] = analysis
                
                analysis_path = os.path.join(self.debug_folder, f"{base_filename}_analysis.txt")
                with open(analysis_path, 'w', encoding='utf-8') as f:
                    f.write(f"Debug Analysis for: {debug_name}\n")
                    f.write(f"Timestamp: {timestamp}\n")
                    f.write(f"URL: {driver.current_url}\n")
                    f.write(f"Title: {driver.title}\n\n")
                    
                    f.write("=== ELEMENT ANALYSIS ===\n")
                    for element_type, elements in analysis.items():
                        f.write(f"\n{element_type.upper()}:\n")
                        for element in elements[:10]:  # Limit to first 10
                            f.write(f"  - {element}\n")
                
                results['analysis_path'] = analysis_path
                results['files_created'].append(analysis_path)
                print(f"   📊 Analysis saved: {analysis_path}")
            
            print(f"✅ Debug state captured for: {debug_name}")
            return results
            
        except Exception as e:
            print(f"❌ Error capturing debug state: {e}")
            return {
                'error': str(e),
                'timestamp': timestamp,
                'debug_name': debug_name
            }
    
    def _analyze_page_elements(self, driver) -> Dict[str, list]:
        """
        Analyze page elements for debugging.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            Dict[str, list]: Analysis of page elements
        """
        analysis = {
            'buttons': [],
            'inputs': [],
            'links': [],
            'forms': [],
            'errors': [],
            'messages': []
        }
        
        try:
            # Find buttons
            buttons = driver.find_elements(By.TAG_NAME, "button")
            buttons.extend(driver.find_elements(By.XPATH, "//input[@type='submit']"))
            for btn in buttons:
                try:
                    text = btn.text or btn.get_attribute("value") or btn.get_attribute("id")
                    if text:
                        analysis['buttons'].append(text.strip()[:50])
                except:
                    pass
            
            # Find input fields
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                try:
                    input_type = inp.get_attribute("type")
                    input_id = inp.get_attribute("id")
                    input_name = inp.get_attribute("name")
                    placeholder = inp.get_attribute("placeholder")
                    
                    desc = f"{input_type} - ID:{input_id} Name:{input_name} Placeholder:{placeholder}"
                    analysis['inputs'].append(desc[:100])
                except:
                    pass
            
            # Find links
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                try:
                    text = link.text.strip()
                    href = link.get_attribute("href")
                    if text and href:
                        analysis['links'].append(f"{text[:30]} -> {href[:50]}")
                except:
                    pass
            
            # Find forms
            forms = driver.find_elements(By.TAG_NAME, "form")
            for form in forms:
                try:
                    form_id = form.get_attribute("id")
                    form_action = form.get_attribute("action")
                    analysis['forms'].append(f"ID:{form_id} Action:{form_action}")
                except:
                    pass
            
            # Look for error messages
            error_selectors = [
                ".error", ".alert-danger", ".alert-error", 
                "[class*='error']", "[class*='danger']"
            ]
            for selector in error_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text:
                            analysis['errors'].append(text[:100])
                except:
                    pass
            
            # Look for success/info messages
            message_selectors = [
                ".message", ".alert", ".notification",
                "[class*='message']", "[class*='alert']"
            ]
            for selector in message_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text:
                            analysis['messages'].append(text[:100])
                except:
                    pass
            
        except Exception as e:
            analysis['analysis_error'] = str(e)
        
        return analysis
    
    def log_action(self, action: str, details: str = "", level: str = "INFO"):
        """
        Log an action with timestamp.
        
        Args:
            action (str): The action being performed
            details (str): Additional details
            level (str): Log level (INFO, WARN, ERROR)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {action}"
        if details:
            log_entry += f" - {details}"
        
        print(log_entry)
        
        # Optionally save to log file
        try:
            log_file = os.path.join(self.debug_folder, "gym_bot.log")
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except:
            pass  # Don't fail if logging fails

# Global debug manager instance
_debug_manager = None

def get_debug_manager() -> DebugManager:
    """
    Get a debug manager instance.
    
    Returns:
        DebugManager: Debug manager instance
    """
    global _debug_manager
    
    if _debug_manager is None:
        _debug_manager = DebugManager()
    
    return _debug_manager

def debug_page_state(
    driver, 
    debug_name: str,
    include_screenshot: bool = True,
    include_html: bool = True,
    include_analysis: bool = True
) -> Dict[str, Any]:
    """
    Capture page state for debugging.
    
    Args:
        driver: WebDriver instance
        debug_name (str): Name for the debug session
        include_screenshot (bool): Whether to take a screenshot
        include_html (bool): Whether to save HTML source
        include_analysis (bool): Whether to analyze page elements
        
    Returns:
        Dict[str, Any]: Debug information and file paths
    """
    manager = get_debug_manager()
    return manager.capture_page_state(
        driver, debug_name, include_screenshot, include_html, include_analysis
    )

def log_action(action: str, details: str = "", level: str = "INFO"):
    """
    Log an action with timestamp.
    
    Args:
        action (str): The action being performed
        details (str): Additional details
        level (str): Log level (INFO, WARN, ERROR)
    """
    manager = get_debug_manager()
    manager.log_action(action, details, level)
