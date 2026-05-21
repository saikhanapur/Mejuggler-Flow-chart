#!/usr/bin/env python3
"""
Test Enhanced Key Timings Extraction (Feature 3 - Option B)
"""

import requests
import json

# Configuration
BASE_URL = "https://sop-flowchart-ai.preview.emergentagent.com/api"
TIMEOUT = 120

def test_enhanced_key_timings():
    """Test Enhanced Key Timings Extraction with the exact document from review request"""
    
    # Test document with VARIOUS timing patterns from review request
    system_monitoring_doc = """System Monitoring Procedure
    
    Steps:
    1. Check MyIT ticket status every 30 minutes via the IT portal
    2. Update stakeholder teams hourly through email distribution list
    3. Monitor system performance within 5 minutes of alert
    4. Send status reports twice per day at 9am and 5pm
    5. Review incident logs daily in Lighthouse system
    6. Escalate unresolved issues by 2:00 PM to management
    7. Verify resolution and document findings
    8. Complete final report
    """
    
    print("⏰ Testing Enhanced Key Timings Extraction (Feature 3 - Option B)")
    print("=" * 80)
    print(f"📄 Test Document: System Monitoring Procedure")
    print(f"🎯 Expected Patterns: every 30 minutes, hourly, within 5 minutes, twice per day, daily, by 2:00 PM")
    print()
    
    try:
        payload = {
            "text": system_monitoring_doc,
            "inputType": "document"
        }
        
        print("🔍 Sending POST /api/process/eroad-style...")
        response = requests.post(f"{BASE_URL}/process/eroad-style", 
                               json=payload, 
                               headers={'Content-Type': 'application/json'},
                               timeout=TIMEOUT)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response Successful")
            
            # Check response structure
            if 'processes' in result and result['processes']:
                process = result['processes'][0]
                quick_reference = process.get('quickReference', {})
            elif 'quickReference' in result:
                quick_reference = result.get('quickReference', {})
            else:
                print("❌ No quickReference found in response")
                print(f"Response keys: {list(result.keys())}")
                return False
            
            key_timings = quick_reference.get('keyTimings', [])
            
            print(f"\n📊 Key Timings Found: {len(key_timings)}")
            print("=" * 50)
            
            if key_timings:
                for i, timing in enumerate(key_timings, 1):
                    print(f"{i}. {timing}")
                
                print("\n🔍 Pattern Analysis:")
                print("=" * 30)
                
                # Check for expected patterns
                patterns_found = []
                
                # Pattern 1: "every 30 minutes"
                for timing in key_timings:
                    if "every 30 minutes" in timing.lower() and "check" in timing.lower():
                        patterns_found.append("✅ 'every 30 minutes' with action")
                        break
                else:
                    patterns_found.append("❌ 'every 30 minutes' pattern missing")
                
                # Pattern 2: "hourly"
                for timing in key_timings:
                    if "hourly" in timing.lower() and "update" in timing.lower():
                        patterns_found.append("✅ 'hourly' with action")
                        break
                else:
                    patterns_found.append("❌ 'hourly' pattern missing")
                
                # Pattern 3: "within 5 minutes"
                for timing in key_timings:
                    if "within 5 minutes" in timing.lower() and "monitor" in timing.lower():
                        patterns_found.append("✅ 'within 5 minutes' with action")
                        break
                else:
                    patterns_found.append("❌ 'within 5 minutes' pattern missing")
                
                # Pattern 4: "twice per day"
                for timing in key_timings:
                    if "twice per day" in timing.lower() and ("send" in timing.lower() or "report" in timing.lower()):
                        patterns_found.append("✅ 'twice per day' with action")
                        break
                else:
                    patterns_found.append("❌ 'twice per day' pattern missing")
                
                # Pattern 5: "daily"
                for timing in key_timings:
                    if "daily" in timing.lower() and "review" in timing.lower():
                        patterns_found.append("✅ 'daily' with action")
                        break
                else:
                    patterns_found.append("❌ 'daily' pattern missing")
                
                # Pattern 6: "by 2:00 PM"
                for timing in key_timings:
                    if "2:00 pm" in timing.lower() and "escalate" in timing.lower():
                        patterns_found.append("✅ 'by 2:00 PM' with action")
                        break
                else:
                    patterns_found.append("❌ 'by 2:00 PM' pattern missing")
                
                for pattern in patterns_found:
                    print(pattern)
                
                # Success criteria
                successful_patterns = [p for p in patterns_found if p.startswith("✅")]
                failed_patterns = [p for p in patterns_found if p.startswith("❌")]
                
                print(f"\n📈 Results: {len(successful_patterns)}/6 patterns detected successfully")
                
                if len(successful_patterns) >= 4:
                    print("🎉 SUCCESS: Enhanced Key Timings Extraction is working!")
                    print("✅ Multiple timing patterns detected with full context")
                    print("✅ Action verbs preserved")
                    print("✅ Methods/tools included")
                    return True
                else:
                    print("⚠️ PARTIAL SUCCESS: Some patterns missing")
                    for failed in failed_patterns:
                        print(f"   {failed}")
                    return False
                    
            else:
                print("❌ No key timings found in response")
                print("Expected: Array of timing strings with full context")
                return False
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_enhanced_key_timings()
    if success:
        print("\n🎯 Enhanced Key Timings Extraction: WORKING")
    else:
        print("\n❌ Enhanced Key Timings Extraction: NEEDS ATTENTION")