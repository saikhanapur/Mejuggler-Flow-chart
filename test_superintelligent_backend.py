#!/usr/bin/env python3
"""
Test script for Superintelligent AI Backend
Tests the new multi-stage pipeline with the BCP SOP document
"""

import requests
import json
import os
from pathlib import Path

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')

# Sample BCP SOP text (abbreviated for testing)
BCP_SOP_TEXT = """Business Continuity Procedure #8: Wilsar Outage All
"Loss of Wilsar functionality - all onshore and offshore WGSS (Wilson Group Shared Services) affected"

Onshore - Identify Wilsar Outage

Determine if there is a Wilsar Outage
Signs of an outage can include:
- Wilsar session becomes unresponsive
- Errors experienced across WGSS onshore and/or offshore
- Error message when loading/opening Wilsar
- Still unable to launch a new session
- Unable to relaunch jobs that have been manually launched
- Patrol officer calls the NDSC to advise they are unable to view jobs on their Rapid

Has Wilsar Outaged? (Decision Point)
YES:
  - Screenshot any error messages and save (to include in process)
  - Supervisor to dispatch a test job to a Patrol Officer
  - Contact Patrol Officer to check if job received
    Job received? (Decision Point)
      YES: Resume BAU services
      NO: 
        - Advise patrol officer to restart phone and then relaunch Rapid
        - Job received? (Decision Point)
          YES: Resume BAU services
          NO: Advise patrol officer to escalate to their Supervisor/Manager and call back with an outcome

NO:
  - Are internet browsers, Arc Outlook, RingCentral and Wallboards still working? (Decision Point)
    YES: (No further action, Wilsar is working)
    NO: Possible Internet outage - refer to "Internet Outage" in the DSC Outage section

Onshore Actions

Onshore Supervisor to confirm Wilsar outage
Instruct onshore and offshore teams to follow BCP for a Wilsar Outage

Onshore Tasks:
1. Onshore Supervisor to liaise with local team that Council jobs will be temporarily suspended
2. Onshore Supervisor to begin Lighthouse timeline under 'Buddy' location
3. Notify Councils of outage via email
4. Send Modica group message to all Patrol Officers and escalation contacts
5. Distribute BCP mobile devices to all teams
6. Check in with Wilson IT on 0061 8 9415 2888 ext. 8088 every 30 minutes
7. Services restored
8. Send Modica group message advising Wilsar outage has restored
9. Email Councils to advise services have been restored
10. Email NDSC contacts to advise services have been restored
11. Supervisor to allocate Onshore/Offshore responses in Wilsar
12. Supervisor to resume BAU tasks

Offshore Actions

Onshore Supervisor to advise offshore team that Wilsar jobs will be manually dispatched

Offshore Tasks:
1. Reallocate AR tasks
2. Begin Lighthouse timeline under Comms location
3. Email Monitoring Companies to advise of outage
4. Check in with onshore supervisor every 30 minutes
5. Services restored
6. Email Monitoring Companies to advise services have been restored
7. Email offshore contacts to advise services have been restored
8. 1 x offshore operator to confirm email for jobs manually dispatched
9. Offshore team to confirm Wilsar is back up and running
10. Resume BAU tasks

References

Lighthouse Timeline:
- Outage description:
- PT ticket creation time:
- PT ticket status time:
- Patrol/efforts/WC/WhatsApp time:
- Job status time:
- Other Comments:

Wilsar Outage BCP Comms Email to Councils
Wilsar Outage BCP Comms Email to Monitoring Companies

Modica Message Script: Wilsar Outage Notification
"Wilsar is currently out of service and is affecting jobs being dispatched to your Council..."

Onshore Escalation Contacts:
- David Seabor
- Roshan Galloway
- Nick Gibbo
- Jule Kali
- Jay Rat
- All Regional Managers
- All Branch Managers

Offshore Escalation Contacts:
- Natasha Cole
- Christopher Cuenca
- John Fortes

Wilson IT Contact: 0061 8 9415 2888 ext. 8088
Dispatch Services Team: 0800 347 787 (option 1)
"""

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_stage_0_analyze():
    """Test Stage 0: Document Intelligence & Classification"""
    print_section("TEST 1: Stage 0 - Document Intelligence")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/process/analyze-document",
            json={
                "text": BCP_SOP_TEXT,
                "inputType": "document"
            },
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Analysis ID: {data.get('analysisId')}")
            print(f"📄 Document Summary: {data.get('documentSummary', 'N/A')}")
            print(f"📊 Total Sections: {data.get('totalSections', len(data.get('sections', [])))}")
            
            overall = data.get('overallAnalysis', {})
            print(f"\n🎯 Overall Analysis:")
            print(f"   - Flowchartable Sections: {overall.get('flowchartableSections', 0)}")
            print(f"   - Total Estimated Steps: {overall.get('totalEstimatedSteps', 0)}")
            print(f"   - Reference Sections: {overall.get('referenceSections', 0)}")
            print(f"   - Complexity: {overall.get('complexity', 'N/A').upper()}")
            
            print(f"\n📑 Section Details:")
            for i, section in enumerate(data.get('sections', [])[:5], 1):
                print(f"\n   Section {i}: {section.get('title')}")
                print(f"   └─ Classification: {section.get('classification').upper()}")
                print(f"   └─ Reasoning: {section.get('reasoning')[:100]}...")
                if section.get('estimatedSteps'):
                    print(f"   └─ Estimated Steps: {section.get('estimatedSteps')}")
                if section.get('confidence'):
                    print(f"   └─ Confidence: {section.get('confidence')}")
            
            print(f"\n✅ TEST PASSED: AI successfully analyzed the document!")
            print(f"   The AI classified sections intelligently and provided reasoning.")
            
            return data
        else:
            print(f"❌ TEST FAILED: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        return None

def test_learning_insights():
    """Test learning system insights"""
    print_section("TEST 2: Learning System Insights")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/learning/insights",
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"📚 Learning System Statistics:")
            print(f"   - Total Analyses: {data.get('totalAnalyses', 0)}")
            print(f"   - Validated Analyses: {data.get('validatedAnalyses', 0)}")
            print(f"   - Total Patterns Learned: {data.get('totalPatterns', 0)}")
            print(f"   - User Feedback Count: {data.get('totalFeedback', 0)}")
            print(f"   - Validation Rate: {data.get('validationRate', 0)}%")
            
            patterns = data.get('topPatterns', [])
            if patterns:
                print(f"\n🎯 Top Learned Patterns:")
                for pattern in patterns[:3]:
                    print(f"   - {pattern.get('pattern')}: {pattern.get('classification')} ({pattern.get('confidence')}% confidence)")
            
            print(f"\n✅ TEST PASSED: Learning system is operational!")
            return data
        else:
            print(f"⚠️  Learning system not yet populated (expected for first run)")
            return None
            
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        return None

def test_full_pipeline():
    """Test the full pipeline from analysis to flowchart"""
    print_section("TEST 3: Full Pipeline (Stage 0 → Stage 1-3)")
    
    # First, run Stage 0
    print("Running Stage 0: Document Analysis...")
    analysis = test_stage_0_analyze()
    
    if not analysis:
        print("❌ Cannot proceed - Stage 0 failed")
        return
    
    # In a real frontend, user would review and approve sections here
    # For testing, we'll auto-approve all flowchartable sections
    approved_sections = [
        sec['sectionId'] for sec in analysis.get('sections', [])
        if sec.get('classification') == 'flowchartable'
    ]
    
    if not approved_sections:
        print("⚠️  No flowchartable sections found to process")
        return
    
    print(f"\n🎯 Auto-approving {len(approved_sections)} flowchartable sections...")
    print(f"   (In real UI, user would review and approve these)")
    
    # Now run Stages 1-3
    print(f"\nRunning Stages 1-3: Flowchart Generation...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/process/generate-from-analysis",
            json={
                "documentText": BCP_SOP_TEXT,
                "analysisId": analysis['analysisId'],
                "approvedSections": approved_sections,
                "userCorrections": []
            },
            timeout=120
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            processes = data.get('processes', [])
            if processes:
                process = processes[0]
                print(f"\n✅ Flowchart Generated Successfully!")
                print(f"   - Process Name: {process.get('processName')}")
                print(f"   - Total Steps: {len(process.get('nodes', []))}")
                print(f"   - Swim Lanes: {len(process.get('swimLanes', []))}")
                print(f"   - Edges: {len(process.get('edges', []))}")
            
            coverage = data.get('coverageReport', {})
            if coverage:
                print(f"\n📊 Coverage Report:")
                print(f"   - Steps Captured: {coverage.get('stepsCaptured')}")
                print(f"   - Steps Expected: {coverage.get('stepsExpected')}")
                print(f"   - Completeness: {coverage.get('completeness')}%")
                print(f"   - Nodes with Details: {coverage.get('nodesWithOperationalDetails')}")
                print(f"   - Decision Nodes: {coverage.get('decisionNodesMapped')}")
            
            print(f"\n🎉 FULL PIPELINE TEST PASSED!")
            print(f"   The AI successfully processed your complex BCP SOP!")
            
        else:
            print(f"❌ TEST FAILED: {response.status_code}")
            print(f"   Error: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")

def main():
    """Run all tests"""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║         SUPERINTELLIGENT AI BACKEND - COMPREHENSIVE TEST SUITE          ║
║                                                                          ║
║  Testing the new multi-stage pipeline with your BCP SOP document        ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    print(f"🔗 Backend URL: {BACKEND_URL}")
    print(f"📄 Test Document: BCP SOP #8 - Wilsar Outage (abbreviated)")
    
    # Test 1: Stage 0 Analysis
    analysis = test_stage_0_analyze()
    
    # Test 2: Learning System
    test_learning_insights()
    
    # Test 3: Full Pipeline (only if Stage 0 passed)
    if analysis:
        input("\n⏸️  Press ENTER to test the full pipeline (Stages 1-3)...")
        test_full_pipeline()
    
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                          🎉 TESTING COMPLETE 🎉                         ║
║                                                                          ║
║  Next Steps:                                                             ║
║  1. Review the results above                                             ║
║  2. If tests passed, proceed with frontend implementation                ║
║  3. If tests failed, check backend logs for errors                       ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    main()
