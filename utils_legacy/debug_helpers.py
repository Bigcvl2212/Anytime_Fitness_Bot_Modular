"""
Advanced Debug Helpers - VERIFIED WORKING CODE FROM 20250627_WORKING.PY
Contains the proven debugging functions that capture comprehensive page state.
"""

import os
import json
from datetime import datetime
from selenium.webdriver.common.by import By


def debug_page_state(driver, debug_name):
    """
    Captures comprehensive page state for debugging - HTML, screenshot, and filter analysis.
    Returns paths to created debug files for immediate analysis.
    
    VERIFIED WORKING CODE FROM 20250627_WORKING.PY
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"debug_{debug_name}_{timestamp}"
        
        results = {
            'timestamp': timestamp,
            'files_created': [],
            'current_url': driver.current_url,
            'page_title': driver.title
        }
        
        # 1. Take screenshot
        try:
            screenshot_path = f"{base_filename}_screenshot.png"
            driver.save_screenshot(screenshot_path)
            results['files_created'].append(screenshot_path)
            print(f"   📸 Screenshot saved: {screenshot_path}")
        except Exception as e:
            print(f"   ⚠️ Could not take screenshot: {e}")
        
        # 2. Save page source (HTML)
        try:
            html_path = f"{base_filename}_page_source.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            results['files_created'].append(html_path)
            print(f"   📄 HTML source saved: {html_path}")
        except Exception as e:
            print(f"   ⚠️ Could not save HTML: {e}")
        
        # 3. Capture current state info
        try:
            info_path = f"{base_filename}_state_info.json"
            state_info = {
                'url': driver.current_url,
                'title': driver.title,
                'timestamp': timestamp,
                'window_size': driver.get_window_size(),
                'available_iframes': [],
                'visible_forms': [],
                'filter_elements': []
            }
            
            # Check for iframes
            try:
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                for i, iframe in enumerate(iframes):
                    iframe_info = {
                        'index': i,
                        'name': iframe.get_attribute('name'),
                        'src': iframe.get_attribute('src'),
                        'visible': iframe.is_displayed()
                    }
                    state_info['available_iframes'].append(iframe_info)
            except:
                pass
            
            # Check for forms
            try:
                forms = driver.find_elements(By.TAG_NAME, "form")
                for i, form in enumerate(forms):
                    form_info = {
                        'index': i,
                        'action': form.get_attribute('action'),
                        'method': form.get_attribute('method'),
                        'visible': form.is_displayed()
                    }
                    state_info['visible_forms'].append(form_info)
            except:
                pass
            
            # Check for filter elements (if on training page)
            try:
                filter_elements = driver.find_elements(By.CSS_SELECTOR, "[id*='filter'], [class*='filter'], [id*='dropdown'], [class*='dropdown']")
                for elem in filter_elements[:10]:  # Limit to first 10
                    elem_info = {
                        'tag': elem.tag_name,
                        'id': elem.get_attribute('id'),
                        'class': elem.get_attribute('class'),
                        'text': elem.text[:50] if elem.text else '',
                        'visible': elem.is_displayed()
                    }
                    state_info['filter_elements'].append(elem_info)
            except:
                pass
            
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(state_info, f, indent=2)
            results['files_created'].append(info_path)
            print(f"   📊 State info saved: {info_path}")
            
        except Exception as e:
            print(f"   ⚠️ Could not save state info: {e}")
        
        print(f"   ✅ Debug capture complete for '{debug_name}' - {len(results['files_created'])} files created")
        return results
        
    except Exception as e:
        print(f"   ❌ Debug capture failed: {e}")
        return None


def force_close_all_dropdowns(driver):
    """
    Force close all open dropdowns to ensure clean state.
    
    VERIFIED WORKING CODE FROM 20250627_WORKING.PY
    """
    try:
        # Try to close any open dropdowns by clicking outside
        driver.execute_script("document.body.click();")
        return True
    except:
        return False


def wait_for_dropdown_stable(driver, timeout=5):
    """
    Wait for dropdown to stabilize before interacting.
    
    VERIFIED WORKING CODE FROM 20250627_WORKING.PY
    """
    import time
    try:
        time.sleep(timeout)
        return True
    except:
        return False
