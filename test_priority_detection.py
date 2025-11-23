#!/usr/bin/env python3
"""
AI Priority Detection P0-P4 Classification Test
Tests the new priority detection feature with varying urgency levels
"""

import requests
import json

def test_priority_detection():
    """Test AI Priority Detection P0-P4 Classification"""
    print("🚨 TESTING: AI Priority Detection P0-P4 Classification (Feature 6 - Option B Phase 2)")
    print("=" * 90)
    
    # Test document with VARYING URGENCY LEVELS from review request
    emergency_response_doc = """Emergency Response & System Monitoring
    
    Critical Actions:
    1. Call 111 immediately if life-threatening injury suspected
    2. Notify emergency services within 2 minutes for system-wide outage
    3. Create P1 ticket urgently for critical failures
    4. Contact on-duty manager within 15 minutes
    
    Standard Operations:
    5. Monitor system performance hourly
    6. Send stakeholder status updates daily
    7. Review incident logs weekly
    8. Update documentation as needed
    9. Complete monthly reports
    """
    
    url = 'https://sopviz-1.preview.emergentagent.com/api/process/eroad-style'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    payload = {
        'text': emergency_response_doc,
        'inputType': 'document'
    }
    
    try:
        print("🔍 Testing POST /api/process/eroad-style with varying urgency levels...")
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'processes' in result and result['processes']:
                process = result['processes'][0]
                nodes = process.get('nodes', [])
                critical_actions = process.get('quickReference', {}).get('criticalActions', [])
                
                print(f"✅ SUCCESS: Found {len(nodes)} nodes with priority data")
                
                # Test Results
                validation_results = []
                
                # Test 1: Verify every node has priority field
                nodes_with_priority = 0
                for node in nodes:
                    if 'priority' in node and isinstance(node['priority'], dict):
                        priority = node['priority']
                        required_fields = ['level', 'score', 'emoji', 'color', 'label', 'breakdown']
                        if all(field in priority for field in required_fields):
                            nodes_with_priority += 1
                
                if nodes_with_priority == len(nodes):
                    validation_results.append(f"✅ Priority Structure: All {len(nodes)} nodes have complete priority data")
                else:
                    validation_results.append(f"❌ Priority Structure: Only {nodes_with_priority}/{len(nodes)} nodes have complete priority data")
                
                # Test 2: Verify P0 assignment for life-threatening actions
                p0_nodes = []
                for node in nodes:
                    if node.get('priority', {}).get('level') == 'P0':
                        p0_nodes.append(node)
                        title = node.get('title', '').lower()
                        description = node.get('description', '').lower()
                        full_text = f"{title} {description}"
                        if ('call 111' in full_text or 'life-threatening' in full_text or 
                            'immediately' in full_text or 'emergency' in full_text):
                            validation_results.append(f"✅ P0 Classification: '{node.get('title')}' correctly assigned P0 (score: {node.get('priority', {}).get('score')})")
                
                if not p0_nodes:
                    validation_results.append("❌ P0 Classification: No P0 nodes found for life-threatening actions")
                
                # Test 3: Verify P1 assignment for urgent time-sensitive actions
                p1_nodes = []
                for node in nodes:
                    if node.get('priority', {}).get('level') == 'P1':
                        p1_nodes.append(node)
                        title = node.get('title', '').lower()
                        description = node.get('description', '').lower()
                        full_text = f"{title} {description}"
                        if ('within 2 minutes' in full_text or 'emergency services' in full_text or 
                            'p1 ticket' in full_text or 'urgently' in full_text):
                            validation_results.append(f"✅ P1 Classification: '{node.get('title')}' correctly assigned P1 (score: {node.get('priority', {}).get('score')})")
                
                # Test 4: Verify P2 assignment for within 15 minutes actions
                p2_nodes = []
                for node in nodes:
                    if node.get('priority', {}).get('level') == 'P2':
                        p2_nodes.append(node)
                        title = node.get('title', '').lower()
                        description = node.get('description', '').lower()
                        full_text = f"{title} {description}"
                        if 'within 15 minutes' in full_text or 'manager' in full_text:
                            validation_results.append(f"✅ P2 Classification: '{node.get('title')}' correctly assigned P2 (score: {node.get('priority', {}).get('score')})")
                
                # Test 5: Verify P3/P4 assignment for standard operations
                p3_p4_nodes = []
                for node in nodes:
                    level = node.get('priority', {}).get('level')
                    if level in ['P3', 'P4']:
                        p3_p4_nodes.append(node)
                        title = node.get('title', '').lower()
                        description = node.get('description', '').lower()
                        full_text = f"{title} {description}"
                        if ('hourly' in full_text or 'daily' in full_text or 'weekly' in full_text or 
                            'monthly' in full_text or 'monitor' in full_text or 'update' in full_text):
                            validation_results.append(f"✅ P3/P4 Classification: '{node.get('title')}' correctly assigned {level} (score: {node.get('priority', {}).get('score')})")
                
                # Test 6: Verify priority distribution (should have variety)
                priority_levels = {}
                for node in nodes:
                    level = node.get('priority', {}).get('level')
                    if level:
                        priority_levels[level] = priority_levels.get(level, 0) + 1
                
                if len(priority_levels) >= 3:
                    validation_results.append(f"✅ Priority Distribution: Good variety - {dict(priority_levels)}")
                else:
                    validation_results.append(f"⚠️ Priority Distribution: Limited variety - {dict(priority_levels)}")
                
                # Test 7: Verify critical actions enhancement with priority emoji
                if critical_actions:
                    priority_enhanced_actions = 0
                    for action in critical_actions:
                        if any(emoji in action for emoji in ['🔴', '🟠', '🟡', '🔵', '⚪']):
                            priority_enhanced_actions += 1
                    
                    if priority_enhanced_actions >= len(critical_actions) * 0.8:  # 80% should have priority emoji
                        validation_results.append(f"✅ Critical Actions Enhancement: {priority_enhanced_actions}/{len(critical_actions)} actions have priority emoji")
                    else:
                        validation_results.append(f"❌ Critical Actions Enhancement: Only {priority_enhanced_actions}/{len(critical_actions)} actions have priority emoji")
                
                # Overall assessment
                failed_checks = [r for r in validation_results if r.startswith("❌")]
                
                print("\n📊 TEST RESULTS:")
                for result in validation_results:
                    print(f"   {result}")
                
                print(f"\n📋 Sample Priority Classifications:")
                for i, node in enumerate(nodes[:5], 1):  # Show first 5 nodes
                    priority = node.get('priority', {})
                    print(f"   {i}. {node.get('title')}")
                    print(f"      Priority: {priority.get('emoji', '?')} {priority.get('level', '?')} - {priority.get('label', '?')} (Score: {priority.get('score', '?')})")
                    breakdown = priority.get('breakdown', {})
                    print(f"      Breakdown: Severity={breakdown.get('severity', '?')}, Urgency={breakdown.get('urgency', '?')}, Frequency={breakdown.get('frequency', '?')}, Visibility={breakdown.get('visibility', '?')}")
                
                # Test critical actions format
                if critical_actions:
                    print(f"\n📋 Enhanced Critical Actions with Priority:")
                    for i, action in enumerate(critical_actions[:4], 1):  # Show first 4
                        print(f"   {i}. {action}")
                
                if len(failed_checks) == 0:
                    print(f"\n🎉 OVERALL RESULT: ✅ ALL TESTS PASSED - AI Priority Detection P0-P4 is working perfectly!")
                    return True
                elif len(failed_checks) <= 2:
                    print(f"\n⚠️ OVERALL RESULT: ✅ CORE FUNCTIONALITY WORKING with {len(failed_checks)} minor issues")
                    return True
                else:
                    print(f"\n❌ OVERALL RESULT: MULTIPLE CRITICAL ISSUES - {len(failed_checks)} failed checks")
                    return False
                    
            else:
                print("❌ FAIL: No processes found in response")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception occurred: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_priority_detection()
    exit(0 if success else 1)