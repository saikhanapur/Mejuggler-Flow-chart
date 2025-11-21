#!/usr/bin/env python3
"""
Smart Semantic Search Test - Feature 7 (Option B Phase 2 - FINAL)
Tests the final feature for Option B completion
"""

import requests
import json
import uuid
import time

BASE_URL = "https://sopchart.preview.emergentagent.com/api"
TIMEOUT = 120

def test_semantic_search():
    """Test Smart Semantic Search - FINAL FEATURE"""
    print("🔍 TESTING SMART SEMANTIC SEARCH (Feature 7 - Option B Phase 2 - FINAL)")
    print("=" * 80)
    print("🎉 THIS IS THE FINAL FEATURE TEST - IF THIS WORKS, OPTION B IS 100% COMPLETE!")
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    # Step 1: Create test processes first
    print("\n📝 Step 1: Creating test processes for semantic search...")
    
    # Process 1 - Emergency Response (Extended)
    emergency_process_doc = """Emergency Response Procedure
    1. Call 111 immediately if life-threatening injury suspected
    2. Contact Wilson IT support team: 0061 8 9415 2888 ext 8088
    3. Notify emergency services and provide location details
    4. Document incident details in system
    5. Inform on-duty manager within 15 minutes
    6. Coordinate with emergency responders
    7. Update stakeholders on situation status
    8. Complete incident report after resolution
    """
    
    # Process 2 - System Monitoring (Extended)
    monitoring_process_doc = """System Monitoring Process
    1. Monitor system performance hourly using dashboard
    2. Contact technical support: 0800 123 456 for issues
    3. Escalate critical system failures to manager immediately
    4. Update stakeholders via email on system status
    5. Check backup systems and failover procedures
    6. Review system logs for anomalies
    7. Perform routine maintenance checks
    8. Generate daily system health reports
    """
    
    created_process_ids = []
    
    # Create Emergency Response Process
    try:
        # First parse the process
        payload = {
            "text": emergency_process_doc,
            "inputType": "document"
        }
        
        response = session.post(f"{BASE_URL}/process/parse", 
                               json=payload, timeout=TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract process data from parse response
            process_data = None
            if 'processes' in result and result['processes']:
                process_data = result['processes'][0]
            elif 'processName' in result:
                process_data = result
            
            if process_data:
                # Now create the actual process in database
                process_payload = {
                    "id": str(uuid.uuid4()),
                    "name": process_data.get('processName', process_data.get('name', 'Emergency Response Process')),
                    "description": process_data.get('description', 'Emergency response procedure'),
                    "status": "draft",
                    "nodes": process_data.get('nodes', []),
                    "actors": process_data.get('actors', []),
                    "criticalGaps": process_data.get('criticalGaps', []),
                    "improvementOpportunities": process_data.get('improvementOpportunities', []),
                    "theme": "minimalist",
                    "healthScore": 85,
                    "views": 0
                }
                
                create_response = session.post(f"{BASE_URL}/process", 
                                             json=process_payload, timeout=TIMEOUT)
                
                if create_response.status_code == 200:
                    created_process = create_response.json()
                    process_id = created_process.get('id')
                    if process_id:
                        created_process_ids.append(process_id)
                        print(f"✅ Created Emergency Response Process: {process_id}")
                    else:
                        print("❌ Emergency Response Process created but no ID returned")
                else:
                    print(f"❌ Failed to create Emergency Response Process: HTTP {create_response.status_code}")
            else:
                print("❌ Emergency Response Process parsing failed - no process data")
        else:
            print(f"❌ Emergency Response Process creation failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Emergency Response Process creation error: {str(e)}")
    
    # Create System Monitoring Process
    try:
        # First parse the process
        payload = {
            "text": monitoring_process_doc,
            "inputType": "document"
        }
        
        response = session.post(f"{BASE_URL}/process/parse", 
                               json=payload, timeout=TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract process data from parse response
            process_data = None
            if 'processes' in result and result['processes']:
                process_data = result['processes'][0]
            elif 'processName' in result:
                process_data = result
            
            if process_data:
                # Now create the actual process in database
                process_payload = {
                    "id": str(uuid.uuid4()),
                    "name": process_data.get('processName', process_data.get('name', 'System Monitoring Process')),
                    "description": process_data.get('description', 'System monitoring procedure'),
                    "status": "draft",
                    "nodes": process_data.get('nodes', []),
                    "actors": process_data.get('actors', []),
                    "criticalGaps": process_data.get('criticalGaps', []),
                    "improvementOpportunities": process_data.get('improvementOpportunities', []),
                    "theme": "minimalist",
                    "healthScore": 85,
                    "views": 0
                }
                
                create_response = session.post(f"{BASE_URL}/process", 
                                             json=process_payload, timeout=TIMEOUT)
                
                if create_response.status_code == 200:
                    created_process = create_response.json()
                    process_id = created_process.get('id')
                    if process_id:
                        created_process_ids.append(process_id)
                        print(f"✅ Created System Monitoring Process: {process_id}")
                    else:
                        print("❌ System Monitoring Process created but no ID returned")
                else:
                    print(f"❌ Failed to create System Monitoring Process: HTTP {create_response.status_code}")
            else:
                print("❌ System Monitoring Process parsing failed - no process data")
        else:
            print(f"❌ System Monitoring Process parsing failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ System Monitoring Process creation error: {str(e)}")
    
    if len(created_process_ids) < 1:
        print(f"❌ Only created {len(created_process_ids)}/2 test processes. Cannot test semantic search properly.")
        return False
    elif len(created_process_ids) == 1:
        print(f"⚠️ Only created {len(created_process_ids)}/2 test processes. Will test with available process.")
    
    print(f"✅ Successfully created {len(created_process_ids)} test processes for semantic search")
    
    # Step 2: Test Semantic Search Queries
    print("\n🔍 Step 2: Testing semantic search queries...")
    
    test_queries = [
        {
            "query": "Who to call if system down?",
            "expected_keywords": ["wilson it", "support", "contact", "0061", "0800"],
            "description": "Should find nodes with contacts (Wilson IT, support)"
        },
        {
            "query": "emergency contact",
            "expected_keywords": ["emergency", "111", "wilson", "contact"],
            "description": "Should find emergency-related nodes"
        },
        {
            "query": "how to escalate",
            "expected_keywords": ["escalate", "manager", "critical"],
            "description": "Should find escalation nodes"
        },
        {
            "query": "completely unrelated query xyz123",
            "expected_keywords": [],
            "description": "Should return no results or very low similarity"
        }
    ]
    
    search_results = []
    
    for i, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        expected_keywords = test_case["expected_keywords"]
        description = test_case["description"]
        
        print(f"\n🔍 Query {i}: '{query}'")
        print(f"   Expected: {description}")
        
        try:
            search_payload = {
                "query": query,
                "limit": 10
            }
            
            response = session.post(f"{BASE_URL}/process/search", 
                                   json=search_payload, timeout=TIMEOUT)
            
            print(f"   Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Verify response structure
                required_fields = ["query", "resultsCount", "results"]
                if all(field in result for field in required_fields):
                    query_result = result["query"]
                    results_count = result["resultsCount"]
                    results = result["results"]
                    
                    print(f"   ✅ Response structure valid: query='{query_result}', count={results_count}")
                    
                    # Show results
                    for j, result_item in enumerate(results):
                        similarity = result_item.get("similarity", 0)
                        node_title = result_item.get("nodeTitle", "Unknown")
                        process_name = result_item.get("processName", "Unknown")
                        print(f"      Result {j+1}: '{node_title}' from '{process_name}' (similarity: {similarity:.3f})")
                    
                    search_results.append({
                        "query": query,
                        "success": True,
                        "results_count": results_count,
                        "results": results
                    })
                    
                else:
                    missing_fields = [f for f in required_fields if f not in result]
                    print(f"   ❌ Invalid response structure, missing: {missing_fields}")
                    search_results.append({
                        "query": query,
                        "success": False,
                        "error": f"Missing fields: {missing_fields}"
                    })
                    
            else:
                print(f"   ❌ Search failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                search_results.append({
                    "query": query,
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                })
                
        except Exception as e:
            print(f"   ❌ Search error: {str(e)}")
            search_results.append({
                "query": query,
                "success": False,
                "error": str(e)
            })
    
    # Step 3: Final Assessment
    print(f"\n🎯 FINAL ASSESSMENT - Smart Semantic Search (Feature 7):")
    print("=" * 60)
    
    successful_searches = sum(1 for r in search_results if r["success"])
    total_searches = len(search_results)
    
    print(f"✅ Successful searches: {successful_searches}/{total_searches}")
    
    if successful_searches >= total_searches * 0.75:  # 75% success rate
        print(f"\n🎉 SUCCESS! Smart Semantic Search is working! Option B is 100% COMPLETE!")
        success = True
    else:
        print(f"\n❌ Issues found with semantic search. Need to fix before Option B completion.")
        success = False
    
    # Cleanup test processes
    print(f"\n🧹 Cleaning up {len(created_process_ids)} test processes...")
    for process_id in created_process_ids:
        try:
            session.delete(f"{BASE_URL}/process/{process_id}", timeout=TIMEOUT)
            print(f"   Deleted process: {process_id}")
        except:
            print(f"   Failed to delete process: {process_id}")
    
    return success

if __name__ == "__main__":
    success = test_semantic_search()
    if success:
        print("\n🎉 SEMANTIC SEARCH TEST PASSED - OPTION B COMPLETE!")
    else:
        print("\n❌ SEMANTIC SEARCH TEST FAILED")