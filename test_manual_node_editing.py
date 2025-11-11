#!/usr/bin/env python3
"""
Manual Node Editing Feature Test - Action Item #2
Tests Tesla-ready manual editing for flowchart nodes
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import time

# Configuration
BASE_URL = "https://sop-wizard-1.preview.emergentagent.com/api"
TIMEOUT = 60

class ManualNodeEditingTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.auth_token = None
        self.test_user_email = "test@superhumanly.ai"
        self.test_user_password = "Test1234!"
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        return success
    
    def test_user_login(self):
        """Login as test user"""
        try:
            # First try to signup (in case user doesn't exist)
            signup_payload = {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "name": "Test User"
            }
            
            signup_response = self.session.post(f"{self.base_url}/auth/signup", 
                                              json=signup_payload, timeout=TIMEOUT)
            # Ignore signup response - user might already exist
            
            # Now try to login
            login_payload = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", 
                                       json=login_payload, timeout=TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result.get('access_token') or result.get('token')
                if self.auth_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}'
                    })
                    return self.log_result("User Login", True, f"Logged in as {self.test_user_email}")
                else:
                    return self.log_result("User Login", False, f"No token received. Response: {result}")
            else:
                return self.log_result("User Login", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_result("User Login", False, f"Error: {str(e)}")
    
    def get_processes(self):
        """Get list of processes"""
        try:
            response = self.session.get(f"{self.base_url}/process", timeout=TIMEOUT)
            if response.status_code == 200:
                processes = response.json()
                return processes
            else:
                print(f"❌ Failed to get processes: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting processes: {str(e)}")
            return []
    
    def test_priority_update(self, process_id, node_id):
        """Test 1: Priority Update"""
        try:
            update_payload = {
                "nodeId": node_id,
                "field": "priority",
                "value": "P0"
            }
            
            response = self.session.patch(f"{self.base_url}/process/{process_id}/node", 
                                        json=update_payload, timeout=TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                
                if (result.get('success') and 
                    'updatedNode' in result):
                    
                    updated_node = result['updatedNode']
                    priority = updated_node.get('priority', {})
                    
                    if (priority.get('level') == 'P0' and 
                        priority.get('manualOverride') == True):
                        
                        # Verify persistence
                        verify_response = self.session.get(f"{self.base_url}/process/{process_id}", 
                                                         timeout=TIMEOUT)
                        if verify_response.status_code == 200:
                            process = verify_response.json()
                            node = next((n for n in process.get('nodes', []) if n.get('id') == node_id), None)
                            if node:
                                node_priority = node.get('priority', {})
                                if isinstance(node_priority, dict) and node_priority.get('level') == 'P0':
                                    return self.log_result("Priority Update", True, 
                                                         "Priority updated to P0 with manualOverride flag and persisted")
                                else:
                                    return self.log_result("Priority Update", False, 
                                                         f"Priority update not persisted. Found: {node_priority}")
                            else:
                                return self.log_result("Priority Update", False, 
                                                     f"Node {node_id} not found in process")
                        else:
                            return self.log_result("Priority Update", False, 
                                                 "Could not verify persistence")
                    else:
                        return self.log_result("Priority Update", False, 
                                             f"Priority not properly updated: {priority}")
                else:
                    return self.log_result("Priority Update", False, 
                                         f"Invalid response structure: {result}")
            else:
                return self.log_result("Priority Update", False, 
                                     f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_result("Priority Update", False, f"Error: {str(e)}")
    
    def test_title_update(self, process_id, node_id):
        """Test 2: Title Update"""
        try:
            new_title = "Updated Test Title"
            update_payload = {
                "nodeId": node_id,
                "field": "title",
                "value": new_title
            }
            
            response = self.session.patch(f"{self.base_url}/process/{process_id}/node", 
                                        json=update_payload, timeout=TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                
                if (result.get('success') and 
                    'updatedNode' in result):
                    
                    updated_node = result['updatedNode']
                    
                    if updated_node.get('title') == new_title:
                        # Check edit history
                        edit_history = updated_node.get('editHistory', [])
                        title_edit = next((e for e in edit_history if e.get('field') == 'title'), None)
                        
                        if title_edit and title_edit.get('newValue') == new_title:
                            # Verify persistence
                            verify_response = self.session.get(f"{self.base_url}/process/{process_id}", 
                                                             timeout=TIMEOUT)
                            if verify_response.status_code == 200:
                                process = verify_response.json()
                                node = next((n for n in process.get('nodes', []) if n.get('id') == node_id), None)
                                if node and node.get('title') == new_title:
                                    return self.log_result("Title Update", True, 
                                                         "Title updated with editHistory and persisted")
                                else:
                                    return self.log_result("Title Update", False, 
                                                         "Title update not persisted")
                            else:
                                return self.log_result("Title Update", False, 
                                                     "Could not verify persistence")
                        else:
                            return self.log_result("Title Update", False, 
                                                 "Edit history not properly tracked")
                    else:
                        return self.log_result("Title Update", False, 
                                             f"Title not updated. Expected: {new_title}, Got: {updated_node.get('title')}")
                else:
                    return self.log_result("Title Update", False, 
                                         f"Invalid response structure: {result}")
            else:
                return self.log_result("Title Update", False, 
                                     f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_result("Title Update", False, f"Error: {str(e)}")
    
    def test_description_update(self, process_id, node_id):
        """Test 3: Description Update"""
        try:
            new_description = "Updated description text"
            update_payload = {
                "nodeId": node_id,
                "field": "description",
                "value": new_description
            }
            
            response = self.session.patch(f"{self.base_url}/process/{process_id}/node", 
                                        json=update_payload, timeout=TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                
                if (result.get('success') and 
                    'updatedNode' in result):
                    
                    updated_node = result['updatedNode']
                    
                    if updated_node.get('description') == new_description:
                        # Verify persistence
                        verify_response = self.session.get(f"{self.base_url}/process/{process_id}", 
                                                         timeout=TIMEOUT)
                        if verify_response.status_code == 200:
                            process = verify_response.json()
                            node = next((n for n in process.get('nodes', []) if n.get('id') == node_id), None)
                            if node and node.get('description') == new_description:
                                return self.log_result("Description Update", True, 
                                                     "Description updated and persisted")
                            else:
                                return self.log_result("Description Update", False, 
                                                     "Description update not persisted")
                        else:
                            return self.log_result("Description Update", False, 
                                                 "Could not verify persistence")
                    else:
                        return self.log_result("Description Update", False, 
                                             f"Description not updated. Expected: {new_description}, Got: {updated_node.get('description')}")
                else:
                    return self.log_result("Description Update", False, 
                                         f"Invalid response structure: {result}")
            else:
                return self.log_result("Description Update", False, 
                                     f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_result("Description Update", False, f"Error: {str(e)}")
    
    def test_error_handling(self, process_id, node_id):
        """Test 4: Error Handling"""
        results = []
        
        # Test 4a: Invalid field
        try:
            update_payload = {
                "nodeId": node_id,
                "field": "invalid",
                "value": "test"
            }
            
            response = self.session.patch(f"{self.base_url}/process/{process_id}/node", 
                                        json=update_payload, timeout=TIMEOUT)
            
            if response.status_code == 400:
                results.append(self.log_result("Error Handling (Invalid Field)", True, 
                                             "Correctly returns 400 for invalid field"))
            else:
                results.append(self.log_result("Error Handling (Invalid Field)", False, 
                                             f"Expected 400, got HTTP {response.status_code}"))
        except Exception as e:
            results.append(self.log_result("Error Handling (Invalid Field)", False, f"Error: {str(e)}"))
        
        # Test 4b: Invalid priority (should default to P3)
        try:
            update_payload = {
                "nodeId": node_id,
                "field": "priority",
                "value": "P99"
            }
            
            response = self.session.patch(f"{self.base_url}/process/{process_id}/node", 
                                        json=update_payload, timeout=TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                priority_level = result.get('updatedNode', {}).get('priority', {}).get('level')
                
                if priority_level == 'P3':
                    results.append(self.log_result("Error Handling (Invalid Priority)", True, 
                                                 "Invalid priority P99 correctly defaulted to P3"))
                else:
                    results.append(self.log_result("Error Handling (Invalid Priority)", False, 
                                                 f"Expected P3 default, got {priority_level}"))
            else:
                results.append(self.log_result("Error Handling (Invalid Priority)", False, 
                                             f"Expected 200 with default, got HTTP {response.status_code}"))
        except Exception as e:
            results.append(self.log_result("Error Handling (Invalid Priority)", False, f"Error: {str(e)}"))
        
        # Test 4c: Non-existent node
        try:
            fake_node_id = "fake-node-id"
            update_payload = {
                "nodeId": fake_node_id,
                "field": "title",
                "value": "test"
            }
            
            response = self.session.patch(f"{self.base_url}/process/{process_id}/node", 
                                        json=update_payload, timeout=TIMEOUT)
            
            if response.status_code == 404:
                results.append(self.log_result("Error Handling (Non-existent Node)", True, 
                                             "Correctly returns 404 for non-existent node"))
            else:
                results.append(self.log_result("Error Handling (Non-existent Node)", False, 
                                             f"Expected 404, got HTTP {response.status_code}"))
        except Exception as e:
            results.append(self.log_result("Error Handling (Non-existent Node)", False, f"Error: {str(e)}"))
        
        # Test 4d: Without auth token
        try:
            # Remove auth header temporarily and clear cookies
            original_headers = self.session.headers.copy()
            original_cookies = self.session.cookies.copy()
            
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            # Clear all cookies to ensure no session_token is sent
            self.session.cookies.clear()
            
            update_payload = {
                "nodeId": node_id,
                "field": "title",
                "value": "unauthorized test"
            }
            
            response = self.session.patch(f"{self.base_url}/process/{process_id}/node", 
                                        json=update_payload, timeout=TIMEOUT)
            
            # Restore headers and cookies
            self.session.headers.update(original_headers)
            self.session.cookies.update(original_cookies)
            
            if response.status_code == 401:
                results.append(self.log_result("Error Handling (No Auth)", True, 
                                             "Correctly returns 401 without auth token"))
            else:
                results.append(self.log_result("Error Handling (No Auth)", False, 
                                             f"Expected 401, got HTTP {response.status_code}: {response.text}"))
        except Exception as e:
            # Restore headers in case of error
            self.session.headers.update(original_headers)
            results.append(self.log_result("Error Handling (No Auth)", False, f"Error: {str(e)}"))
        
        return all(results)
    
    def run_tests(self):
        """Run all Manual Node Editing tests"""
        print("✏️ Manual Node Editing Feature Test - Action Item #2")
        print("=" * 60)
        print("🎯 Testing Tesla-ready manual editing for flowchart nodes")
        print()
        
        # Step 1: Login
        print("🔐 Step 1: User Authentication...")
        if not self.test_user_login():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Step 2: Get processes
        print("\n📋 Step 2: Getting list of processes...")
        processes = self.get_processes()
        if not processes:
            print("❌ No processes available for testing")
            return False
        
        # Step 3: Find process with nodes
        print("\n🎯 Step 3: Selecting process with nodes...")
        test_process = None
        for process in processes:
            if process.get('nodes') and len(process['nodes']) > 0:
                test_process = process
                break
        
        if not test_process:
            print("❌ No processes with nodes found")
            return False
        
        process_id = test_process['id']
        first_node = test_process['nodes'][0]
        first_node_id = first_node['id']
        
        print(f"✅ Selected process: {test_process.get('name', 'Unknown')} (ID: {process_id})")
        print(f"✅ Selected node: {first_node.get('title', 'Unknown')} (ID: {first_node_id})")
        print(f"   Node structure: {json.dumps(first_node, indent=2)[:500]}...")
        
        # Run tests
        print("\n🧪 Running Manual Node Editing Tests...")
        print("-" * 40)
        
        results = []
        
        print("\n🔴 Test 1: Priority Update")
        results.append(self.test_priority_update(process_id, first_node_id))
        
        print("\n📝 Test 2: Title Update")
        results.append(self.test_title_update(process_id, first_node_id))
        
        print("\n📄 Test 3: Description Update")
        results.append(self.test_description_update(process_id, first_node_id))
        
        print("\n⚠️ Test 4: Error Handling")
        results.append(self.test_error_handling(process_id, first_node_id))
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print("\n" + "=" * 60)
        print("📊 MANUAL NODE EDITING TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Manual Node Editing feature is working correctly.")
            return True
        else:
            print("❌ Some tests failed. Manual Node Editing feature needs attention.")
            return False

if __name__ == "__main__":
    tester = ManualNodeEditingTester()
    success = tester.run_tests()
    exit(0 if success else 1)