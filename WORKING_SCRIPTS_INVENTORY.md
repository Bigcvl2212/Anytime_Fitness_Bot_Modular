"""
WORKING SCRIPTS INVENTORY AND ORGANIZATION PLAN
==============================================

This document lists all the working scripts identified from the chat history,
their functions, and where they should be placed in the modular file structure.

CONFIRMED WORKING SCRIPTS:
=========================

1. INVOICE AUTOMATION (PRODUCTION READY)
   Script: send_live_invoices_and_messages.py
   Function: Sends Square invoices via SMS to past due members, excludes Connor Ratzke
   Status: ✅ WORKING - Successfully sent 21 invoices
   Features:
   - Square API integration (PRODUCTION)
   - SMS delivery via mobile phone
   - Connor Ratzke exclusion logic
   - Late fee calculation ($19.50 per missed payment)
   - CSV filtering for 6-30 day and 30+ day overdue
   Target Location: workflows/invoice_automation.py

2. TRAINING PACKAGE API CLIENT (WORKING)
   Script: services/api/enhanced_clubos_client.py
   Function: ClubOS API client with training package endpoints
   Status: ✅ WORKING - Has authentication and package fetching methods
   Features:
   - get_training_packages_for_client()
   - Authentication handling
   - API request management
   Target Location: services/api/clubos_client.py (consolidated)

3. TRAINING PACKAGE TESTS (WORKING)
   Script: tests/test_clubos_training_packages_api.py
   Function: Comprehensive test suite for training package API functionality
   Status: ✅ WORKING - Full test framework
   Features:
   - API endpoint testing
   - Authentication validation
   - Package data validation
   Target Location: tests/training_package_tests.py

4. MEMBER DATA MANAGEMENT (WORKING)
   Script: services/data/member_data.py
   Function: Data handling for training packages and member information
   Status: ✅ WORKING - Has save_training_package_data_comprehensive()
   Features:
   - Training package data saving (JSON + CSV)
   - Member data processing
   - CSV handling utilities
   Target Location: services/data/member_data.py (keep in place)

5. TRAINING WORKFLOW (PARTIAL - SELENIUM)
   Script: workflows/training_workflow.py
   Function: Selenium-based training client scraping and workflow management
   Status: ⚠️ PARTIAL - Has navigation and filtering logic
   Features:
   - ClubOS navigation
   - Training filters
   - Badge-based filtering
   Target Location: workflows/training_selenium.py

6. TRAINING PACKAGE EXTRACTOR (IN PROGRESS)
   Script: extract_active_training_packages.py
   Function: Extract active training packages for clients from CSV using API
   Status: 🔄 IN PROGRESS - Import issues need fixing
   Features:
   - CSV member ID extraction
   - API-based package fetching
   - Active package filtering
   Target Location: scripts/extract_training_packages.py

SCRIPTS TO REMOVE/CONSOLIDATE:
=============================

DUPLICATES/BROKEN:
- extract_training_packages_from_csv.py (duplicate/incomplete)
- fetch_training_agreement_data.py (superseded by API client)
- fetch_training_clients.py (superseded by API client)
- All debug_*.py files (one-time debugging, not needed)
- All test_*.py files except the working test suite
- Multiple master_contact_list_*.csv files (keep only latest)

ORGANIZATION PLAN:
=================

KEEP AND ORGANIZE:
/workflows/
  - invoice_automation.py (from send_live_invoices_and_messages.py)
  - training_selenium.py (from training_workflow.py - cleaned up)

/services/api/
  - clubos_client.py (consolidated from enhanced_clubos_client.py)

/services/data/
  - member_data.py (keep existing, working)

/scripts/
  - extract_training_packages.py (fixed version of extract_active_training_packages.py)

/tests/
  - training_package_tests.py (from test_clubos_training_packages_api.py)

/config/
  - Keep existing secrets.py and constants.py

REMOVE:
- All debug_*.py files
- All test_*.py files except the main training package test
- Duplicate CSV files (keep only latest)
- extract_training_packages_from_csv.py
- Old fetch_training_*.py files
- All HAR analysis files
- All login debugging files

NEXT STEPS:
1. Create organized versions of working scripts
2. Remove duplicate/broken files
3. Test the cleaned up structure
4. Fix import issues in final scripts
"""
