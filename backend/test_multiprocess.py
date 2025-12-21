"""
Quick test for multi-process detection
"""
import asyncio
from multi_process_detector import MultiProcessDetector
import os

# Test documents
SINGLE_PROCESS_DOC = """
Customer Onboarding Process

1. Receive inquiry from customer
2. Send welcome email
3. Schedule onboarding call
4. Complete paperwork
5. Grant system access
"""

MULTIPLE_PROCESSES_DOC = """
## Panic Alert Response
When panic button is pressed:
1. Check if user can speak freely
2. Contact emergency services
3. Stay on line

## Silent Alert Response  
When silent alert triggered:
1. Send text message
2. Wait for response
3. Escalate if no response

## Missed Check-In
When user doesn't check in:
1. Wait 5 minutes
2. Call customer
3. Escalate to supervisor
"""

TEN_STEPS_ONE_PROCESS = """
Equipment Maintenance SOP

1. Inspect equipment daily
2. Log any issues found
3. Report to supervisor
4. Check oil levels
5. Check tire pressure
6. Test brakes
7. Clean exterior
8. Document findings
9. Schedule repairs if needed
10. Complete maintenance log
"""

async def test_detection():
    # Get Emergent LLM key
    from emergent_integrations_manager import get_universal_key
    api_key = get_universal_key()
    
    if not api_key:
        print("❌ ERROR: No API key available")
        return
    
    detector = MultiProcessDetector(api_key)
    
    print("=" * 60)
    print("TEST 1: Single Process (5 steps)")
    print("=" * 60)
    result1 = await detector.detect_processes(SINGLE_PROCESS_DOC)
    print(f"Result: {result1}")
    print(f"✅ PASS" if result1['processCount'] == 1 else f"❌ FAIL - Expected 1, got {result1['processCount']}")
    
    print("\n" + "=" * 60)
    print("TEST 2: Multiple Processes (3 distinct SOPs)")
    print("=" * 60)
    result2 = await detector.detect_processes(MULTIPLE_PROCESSES_DOC)
    print(f"Result: {result2}")
    print(f"✅ PASS" if result2['processCount'] == 3 else f"❌ FAIL - Expected 3, got {result2['processCount']}")
    
    print("\n" + "=" * 60)
    print("TEST 3: Single Process with 10 steps (should NOT be 10 processes!)")
    print("=" * 60)
    result3 = await detector.detect_processes(TEN_STEPS_ONE_PROCESS)
    print(f"Result: {result3}")
    print(f"✅ PASS" if result3['processCount'] == 1 else f"❌ FAIL - Expected 1, got {result3['processCount']}")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    tests_passed = sum([
        result1['processCount'] == 1,
        result2['processCount'] == 3,
        result3['processCount'] == 1
    ])
    print(f"Tests Passed: {tests_passed}/3")
    
    if tests_passed == 3:
        print("🎉 ALL TESTS PASSED - Multi-process detection working correctly!")
    else:
        print("❌ SOME TESTS FAILED - Multi-process detection needs fixing")

if __name__ == "__main__":
    asyncio.run(test_detection())
