#!/usr/bin/env python3
"""
Test Intelligent Critical Actions Extraction Feature (Feature 1 - Option B)
"""

import requests
import json
import uuid
from datetime import datetime, timezone

# Configuration
BASE_URL = "https://flowvision-2.preview.emergentagent.com/api"
TIMEOUT = 120

def test_intelligent_critical_actions_extraction():
    """Test Intelligent Critical Actions Extraction (Feature 1 - Option B) - PRIORITY TEST"""
    print("🎯 TESTING: Intelligent Critical Actions Extraction (Feature 1 - Option B)")
    print("=" * 80)
    
    # Test document with varying urgency levels from review request
    emergency_response_doc = """Emergency Response Procedure
    
    1. Call 111 immediately if injury suspected
    2. Notify on-duty manager within 5 minutes
    3. Document incident details in system
    4. Check every 30 minutes until resolved
    5. Email stakeholder update
    6. Create P1 ticket urgently
    7. Monitor system status
    8. Verify resolution
    9. Complete final report
    """
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    try:
        payload = {
            "text": emergency_response_doc,
            "inputType": "document"
        }
        
        print("📤 Sending request to POST /api/process/eroad-style...")
        response = session.post(f"{BASE_URL}/process/eroad-style", 
                               json=payload, timeout=TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response: 200 OK")
            
            # Check if we have processes array
            if 'processes' in result and result['processes']:
                process = result['processes'][0]
                quick_reference = process.get('quickReference', {})
                critical_actions = quick_reference.get('criticalActions', [])
                
                print(f"\n📋 Extracted Critical Actions ({len(critical_actions)}):")
                for i, action in enumerate(critical_actions, 1):
                    print(f"   {i}. {action}")
                
                validation_results = []
                
                # Test 1: Verify top 5 critical actions extracted
                if len(critical_actions) == 5:
                    validation_results.append("✅ Critical Actions Count: Exactly 5 actions extracted")
                elif len(critical_actions) < 5:
                    validation_results.append(f"⚠️ Critical Actions Count: {len(critical_actions)} actions (acceptable if <5 urgent actions exist)")
                else:
                    validation_results.append(f"❌ Critical Actions Count: {len(critical_actions)} actions (expected max 5)")
                
                # Test 2: Verify urgency ranking (check for emergency/injury concepts first)
                if critical_actions:
                    first_action = critical_actions[0].lower()
                    # Check if highest urgency action relates to emergency/injury (most critical)
                    emergency_keywords = ["emergency", "injury", "111", "call", "medical", "assess"]
                    has_emergency_concept = any(keyword in first_action for keyword in emergency_keywords)
                    
                    if has_emergency_concept and "immediately" in first_action:
                        validation_results.append("✅ Urgency Ranking: Emergency/injury action with 'immediately' is first (highest urgency)")
                    else:
                        validation_results.append(f"⚠️ Urgency Ranking: '{critical_actions[0]}' is first (expected emergency/injury action with 'immediately')")
                    
                    # Check for P1/escalation in top 3
                    top_3_text = " ".join(critical_actions[:3]).lower()
                    if ("p1" in top_3_text or "escalation" in top_3_text) and ("urgent" in top_3_text or "asap" in top_3_text):
                        validation_results.append("✅ Urgency Ranking: P1/escalation with urgency marker in top 3")
                    else:
                        validation_results.append("⚠️ Urgency Ranking: P1/escalation with urgency marker not clearly in top 3")
                    
                    # Check for manager/alert notification in top 5
                    all_actions_text = " ".join(critical_actions).lower()
                    if ("manager" in all_actions_text or "alert" in all_actions_text) and ("5 min" in all_actions_text or "minutes" in all_actions_text):
                        validation_results.append("✅ Urgency Ranking: Manager/alert notification with time window in top 5")
                    else:
                        validation_results.append("⚠️ Urgency Ranking: Manager/alert notification with time window not clearly in top 5")
                
                # Test 3: Verify time windows preserved
                all_actions_text = " ".join(critical_actions).lower()
                time_windows_found = []
                
                if "immediately" in all_actions_text:
                    time_windows_found.append("immediately")
                if "within 5 minutes" in all_actions_text or "5 minutes" in all_actions_text or "(5 min)" in all_actions_text:
                    time_windows_found.append("within 5 minutes")
                if "asap" in all_actions_text or "urgently" in all_actions_text:
                    time_windows_found.append("ASAP/urgently")
                if "30 minutes" in all_actions_text:
                    time_windows_found.append("30 minutes")
                
                if len(time_windows_found) >= 2:
                    validation_results.append(f"✅ Time Windows: {len(time_windows_found)} time constraints preserved: {time_windows_found}")
                else:
                    validation_results.append(f"❌ Time Windows: Only {len(time_windows_found)} time constraints found: {time_windows_found}")
                
                # Test 4: Verify verb-first framing where possible
                verb_first_count = 0
                action_verbs = ['call', 'notify', 'create', 'check', 'email', 'monitor', 'verify', 'complete', 'document']
                
                for action in critical_actions:
                    first_word = action.split()[0].lower() if action.split() else ""
                    if first_word in action_verbs:
                        verb_first_count += 1
                
                if verb_first_count >= 3:
                    validation_results.append(f"✅ Verb-First Framing: {verb_first_count}/{len(critical_actions)} actions start with action verbs")
                else:
                    validation_results.append(f"⚠️ Verb-First Framing: {verb_first_count}/{len(critical_actions)} actions start with action verbs")
                
                # Test 5: Verify NOT just returning all critical status nodes
                if len(critical_actions) <= 5:
                    validation_results.append("✅ Intelligent Extraction: Limited to top 5 (not returning all nodes)")
                else:
                    validation_results.append("❌ Intelligent Extraction: Returning more than 5 actions (may be simple status filter)")
                
                # Test 6: Check recovery steps also extracted
                recovery_steps = quick_reference.get('recoverySteps', [])
                if recovery_steps:
                    validation_results.append(f"✅ Recovery Steps: {len(recovery_steps)} recovery steps extracted")
                else:
                    validation_results.append("⚠️ Recovery Steps: No recovery steps found (may be acceptable)")
                
                # Test 7: Verify response structure
                required_fields = ['criticalActions', 'keyTimings', 'emergencyContacts']
                missing_fields = [field for field in required_fields if field not in quick_reference]
                
                if not missing_fields:
                    validation_results.append("✅ Response Structure: All required quickReference fields present")
                else:
                    validation_results.append(f"❌ Response Structure: Missing fields: {missing_fields}")
                
                # Print validation results
                print(f"\n🔍 Validation Results:")
                for result in validation_results:
                    print(f"   {result}")
                
                # Check backend logs for scoring information
                print(f"\n📊 Additional Information:")
                print(f"   • Process Name: {process.get('name', 'Unknown')}")
                print(f"   • Total Nodes: {len(process.get('nodes', []))}")
                print(f"   • Emergency Contacts: {quick_reference.get('emergencyContacts', {})}")
                print(f"   • Key Timings: {quick_reference.get('keyTimings', [])}")
                
                # Overall assessment
                failed_checks = [r for r in validation_results if r.startswith("❌")]
                warning_checks = [r for r in validation_results if r.startswith("⚠️")]
                
                if not failed_checks:
                    if len(warning_checks) <= 1:
                        print(f"\n🎉 SUCCESS: Intelligent Critical Actions Extraction is working correctly!")
                        return True
                    else:
                        print(f"\n✅ SUCCESS: Core functionality working with minor issues.")
                        return True
                else:
                    print(f"\n❌ FAILURE: Critical issues found:")
                    for failure in failed_checks:
                        print(f"   {failure}")
                    return False
                
            else:
                print("❌ No processes found in response")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_intelligent_critical_actions_extraction()
    if success:
        print(f"\n✅ Test completed successfully!")
    else:
        print(f"\n❌ Test failed!")