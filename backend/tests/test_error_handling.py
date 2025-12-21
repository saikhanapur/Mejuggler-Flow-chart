#!/usr/bin/env python3
"""
Comprehensive Error Handling Tests for SuperHumanly File Upload System
Tests all error scenarios as specified in the review request
"""

import requests
import json
import os
from pathlib import Path

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://process2chart.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class ErrorHandlingTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, test_name, success, details, response_data=None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'response_data': response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
    
    def test_empty_file_upload(self):
        """Test 1: Empty file upload - should return FILE_EMPTY error"""
        try:
            files = {
                'file': ('empty.txt', '', 'text/plain')
            }
            
            response = requests.post(f"{self.base_url}/upload", files=files, timeout=30)
            
            if response.status_code == 400:
                result = response.json()
                detail = result.get('detail', {})
                
                # Verify error structure matches expected format
                expected_fields = ['code', 'title', 'message', 'severity', 'actions', 'retry_available']
                if (detail.get('code') == 'FILE_EMPTY' and 
                    detail.get('title') == 'Empty File' and
                    detail.get('severity') == 'error' and
                    all(field in detail for field in expected_fields)):
                    
                    self.log_result("Empty File Upload", True, 
                                  "Correctly returned FILE_EMPTY error with proper structure")
                    return True
                else:
                    self.log_result("Empty File Upload", False, 
                                  f"Invalid error structure: {detail}")
                    return False
            else:
                self.log_result("Empty File Upload", False, 
                              f"Expected 400, got HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Empty File Upload", False, f"Error: {str(e)}")
            return False
    
    def test_unsupported_file_type(self):
        """Test 2: Unsupported file type - should return UNSUPPORTED_FILE_TYPE error"""
        try:
            # Create fake executable file
            fake_exe_content = b'\x4d\x5a\x90\x00'  # PE header bytes
            files = {
                'file': ('malware.exe', fake_exe_content, 'application/octet-stream')
            }
            
            response = requests.post(f"{self.base_url}/upload", files=files, timeout=30)
            
            if response.status_code == 400:
                result = response.json()
                detail = result.get('detail', {})
                
                # Verify error structure
                if (detail.get('code') == 'UNSUPPORTED_FILE_TYPE' and 
                    detail.get('title') == 'Unsupported File Format' and
                    detail.get('severity') == 'error' and
                    'actions' in detail and
                    detail.get('retry_available') == False):
                    
                    self.log_result("Unsupported File Type", True, 
                                  "Correctly returned UNSUPPORTED_FILE_TYPE error")
                    return True
                else:
                    self.log_result("Unsupported File Type", False, 
                                  f"Invalid error structure: {detail}")
                    return False
            else:
                self.log_result("Unsupported File Type", False, 
                              f"Expected 400, got HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Unsupported File Type", False, f"Error: {str(e)}")
            return False
    
    def test_file_too_large(self):
        """Test 3: File too large - should return FILE_TOO_LARGE error"""
        try:
            # Create large file content (11MB)
            large_content = "A" * (11 * 1024 * 1024)  # 11MB of 'A' characters
            files = {
                'file': ('large_file.txt', large_content, 'text/plain')
            }
            
            response = requests.post(f"{self.base_url}/upload", files=files, timeout=30)
            
            if response.status_code == 400:
                result = response.json()
                detail = result.get('detail', {})
                
                # Verify error structure
                if (detail.get('code') == 'FILE_TOO_LARGE' and 
                    detail.get('title') == 'File Size Exceeds Limit' and
                    detail.get('severity') == 'error' and
                    'actions' in detail and
                    detail.get('retry_available') == False and
                    detail.get('support_contact') == True):
                    
                    self.log_result("File Too Large", True, 
                                  "Correctly returned FILE_TOO_LARGE error")
                    return True
                else:
                    self.log_result("File Too Large", False, 
                                  f"Invalid error structure: {detail}")
                    return False
            else:
                self.log_result("File Too Large", False, 
                              f"Expected 400, got HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("File Too Large", False, f"Error: {str(e)}")
            return False
    
    def test_valid_pdf_upload(self):
        """Test 4: Valid PDF upload - should process successfully or fail gracefully"""
        try:
            # Create a valid PDF with sufficient content
            pdf_content = """%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 200
>>
stream
BT
/F1 12 Tf
72 720 Td
(This is a test PDF document for error handling validation.) Tj
0 -20 Td
(It contains sufficient text content to pass the minimum length requirement.) Tj
0 -20 Td
(The error handling system should process this successfully or return appropriate errors.) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
450
%%EOF"""
            
            files = {
                'file': ('test_document.pdf', pdf_content.encode(), 'application/pdf')
            }
            
            response = requests.post(f"{self.base_url}/upload", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'text' in result and 'method' in result:
                    self.log_result("Valid PDF Upload", True, 
                                  f"Successfully processed PDF via {result.get('method')}")
                    return True
                else:
                    self.log_result("Valid PDF Upload", False, 
                                  f"Invalid success response structure: {result}")
                    return False
            elif response.status_code in [422, 500]:
                # PDF processing might fail due to system limitations
                result = response.json()
                detail = result.get('detail', {})
                
                # These are acceptable error responses for PDF processing
                acceptable_errors = [
                    'TEXT_EXTRACTION_FAILED', 'API_KEY_MISSING', 'OCR_FAILED', 
                    'TEXT_TOO_SHORT', 'UNKNOWN_ERROR'
                ]
                
                if detail.get('code') in acceptable_errors:
                    self.log_result("Valid PDF Upload", True, 
                                  f"PDF processing failed gracefully: {detail.get('code')}")
                    return True
                else:
                    self.log_result("Valid PDF Upload", False, 
                                  f"Unexpected error response: {detail}")
                    return False
            else:
                self.log_result("Valid PDF Upload", False, 
                              f"Unexpected HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Valid PDF Upload", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all error handling tests"""
        print("🛡️ SuperHumanly Error Handling System Tests")
        print("=" * 60)
        print(f"🌐 Testing against: {self.base_url}")
        print()
        
        # Run all tests
        tests = [
            self.test_empty_file_upload,
            self.test_unsupported_file_type,
            self.test_file_too_large,
            self.test_valid_pdf_upload
        ]
        
        results = []
        for test in tests:
            results.append(test())
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"📊 Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {result['test']}: {result['details']}")
        
        if passed == total:
            print("\n🎉 All error handling tests passed!")
            print("✅ Error handling system is working correctly")
        else:
            print(f"\n⚠️ {total - passed} test(s) failed")
            print("❌ Error handling system needs attention")
        
        return passed == total

if __name__ == "__main__":
    tester = ErrorHandlingTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)