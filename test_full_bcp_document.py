#!/usr/bin/env python3
"""
Full BCP SOP Document Test
Tests the superintelligent AI pipeline with the complete BCP document
"""

import requests
import json
import time

BACKEND_URL = "https://process-genius-7.preview.emergentagent.com"

# Full BCP SOP Document
FULL_BCP_TEXT = """Business Continuity Procedure #8
Wilsar Outage All*
"Loss of Wilsar functionality - all onshore and offshore WGSS (Wilson Group Shared Services) affected

Onshore - Identify Wilsar Outage

Determine if there is a Wilsar Outage
Signs of an outage can include:
• Wilsar session becomes unresponsive.
• Error message when loading/executing a Wilsar task.
• Still unable to launch a new Wilsar session after the old has been terminated.
• Patrol officer calls the NDSC to advise they are unable to view jobs on their Rapid.

[Decision Point: Has Wilsar Outage?]
--NO--> Are internet browsers, MS Outlook, RingCentral and Wallboards still working?
  --NO--> Possible Internet outage - refer to "BO Outage" in the DSC
  --YES--> Continue
--YES--> 
  - Screenshot any relevant error messages and save
  - Onshore Supervisor to dispatch a patrol Officer to test job
  - Contact patrol officer to check if job received
    [Decision Point: Job received?]
    --YES--> Resume BAU services
    --NO--> 
      - Advise patrol officer to restart phone and relaunch Rapid
      [Decision Point: Job received?]
      --YES--> Resume BAU services
      --NO--> Advise patrol officer to escalate to their Supervisor/Manager and call back with an outcome

Onshore Actions

Onshore Supervisor to instruct offshore and onboard teams that Wilsar jobs will be completed by phone via service Hub until further notice.

Onshore Tasks:
1. Onshore Supervisor to liaise with local team that Council jobs will be completed by phone via Service Hub until further notice
2. Onshore Supervisor to begin Lighthouse timeline under Buddy location
3. Notify councils of outage via email
4. Send Modica group message to Officers and escalation contacts advising the outage details
5. Distribute 2 x BCP mobile phones to enable teams to assess staffing numbers and reallocate tasks accordingly
6. Check in with Wilson IT on 0061 8 9415 2888 ext. 8088 every 30 minutes for updates until normal services are restored
7. Services restored
8. Send Modica group message to all Patrol Officers and escalation contacts advising the Wilsar outage has restored- returning to BAU
9. Email Councils to advise that services have been restored
10. Email NDSC contacts to advise that services have been restored
11. Supervisor to allocate Onshore new responses in Wilsar for all jobs that were manually dispatched to Lighthouse/Teams during the outage
12. Supervisor to resume BAU tasks

Offshore Actions

Onshore Supervisor to advise offshore team that Wilsar jobs will be manually dispatched by phone via Service Hub until further notice.

Offshore Tasks:
1. Reallocate AR tasks
2. Begin Lighthouse timeline under Comms location
3. Email Monitoring Companies to advise of outage
4. Check in with onshore supervisor every 30 minutes until normal services are restored
5. Services restored
6. Email Monitoring Companies to advise that services have been restored
7. Email offshore contacts to advise that services have been restored
8. 1x offshore operator to confirm in an email that Wilsar is back up and running for your team. MCLs, Patrols and their escalation contacts have been notified. All outage events have been updated. All manual dispatches that were done during the outage have been allocated to an operator in Wilsar.
9. Offshore team to confirm in an email that Wilsar is back up and running for Supervisor
10. Resume BAU tasks

REFERENCES

Lighthouse Timeline:
• Patrol ticket time:
• Outage description:
• PT ticket notification time:
• Patrol notification time:
• Patrol P1/fail/WC/App time:
• Patrol completion time:
• Task allocation details:
• Council notification time:
• Dispatcher notification time:
• Other Comments:

Wilsar Outage BCP Comms Email to Councils
Wilsar Outage BCP Comms Email to Monitoring Companies

Modica Message Script: Wilsar Outage Notification - Council
"Wilsar is currently out of service and is affecting jobs being dispatched to your council. While IT is working to resolve the issue the BCP plan will be enacted. Your jobs via SMS. Rapid app. If you are not receiving jobs to your jobs via SMS. We will provide you with a progress update in 1 hours time."

Onshore Escalation Contacts:
- David Seabor
- Karin Galloway
- Nick Gibby
- Jule Kali
- Jay Rat
- All Regional Managers - refer to escalation sheet for names and contact numbers
- All Branch Managers - refer to escalation sheet for names and contact numbers

Offshore Escalation Contacts:
- Nanette Calko
- Christopher Cuenca
- John Forbes

Email Script:
"This is to let you know that Wilsar services have been restored and BAU has resumed."

Contact Information:
- Wilson IT: 0061 8 9415 2888 ext. 8088
- Check in every 30 minutes for updates

QUICK REFERENCE TIMELINE
1. Raise a P1 ticket with MyIT
2. Begin Timeline in Lighthouse
3. Notify NDSC to Company Awareness
4. Test each job to Wilson's Server
5. After 30 mins contact with Wilson IT, if normal services are not restored
6. Send Modica messages to advise normal services resumed
7. Allocate Additional Onshore/Offshore to queue and surface task
8. Complete manual dispatching all jobs in Lighthouse
9. OUTAGE RESOLVED
10. Send Modica message to advise normal services resumed

National Dispatch Service Centre
Wilsar Outage ALL
28 February 2024
"""

def print_header(title):
    print(f"\n{'='*100}")
    print(f"  {title}")
    print(f"{'='*100}\n")

def test_stage_0_full_document():
    """Test Stage 0 with full BCP document"""
    print_header("STAGE 0: Full Document Intelligence Analysis")
    
    print(f"📄 Document Length: {len(FULL_BCP_TEXT)} characters")
    print(f"📊 Approximate Lines: {len(FULL_BCP_TEXT.split(chr(10)))}")
    print(f"\n🔄 Sending to AI for analysis...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/process/analyze-document",
            json={
                "text": FULL_BCP_TEXT,
                "inputType": "document"
            },
            timeout=120
        )
        
        elapsed = time.time() - start_time
        print(f"⏱️  Analysis Time: {elapsed:.1f} seconds")
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ ANALYSIS SUCCESSFUL!")
            print(f"\n{'─'*100}")
            print(f"📋 Analysis ID: {data.get('analysisId')}")
            print(f"{'─'*100}")
            
            print(f"\n📄 Document Summary:")
            print(f"   {data.get('documentSummary', 'N/A')}")
            
            overall = data.get('overallAnalysis', {})
            print(f"\n🎯 Overall Analysis:")
            print(f"   📊 Complexity: {overall.get('complexity', 'N/A').upper()}")
            print(f"   🔢 Total Estimated Steps: {overall.get('totalEstimatedSteps', 0)}")
            print(f"   ✅ Flowchartable Sections: {overall.get('flowchartableSections', 0)}")
            print(f"   📚 Reference Sections: {overall.get('referenceSections', 0)}")
            print(f"   ℹ️  Contextual Sections: {overall.get('contextualSections', 0)}")
            print(f"   ❌ Excluded Sections: {overall.get('excludedSections', 0)}")
            
            print(f"\n{'─'*100}")
            print(f"📑 SECTION BREAKDOWN ({len(data.get('sections', []))} sections total)")
            print(f"{'─'*100}")
            
            for i, section in enumerate(data.get('sections', []), 1):
                classification = section.get('classification', 'unknown').upper()
                emoji = {
                    'FLOWCHARTABLE': '✅',
                    'REFERENCE': '📚',
                    'CONTEXTUAL': 'ℹ️',
                    'EXCLUDED': '❌'
                }.get(classification, '❓')
                
                print(f"\n{emoji} Section {i}: {section.get('title')}")
                print(f"   └─ Classification: {classification}")
                
                if section.get('estimatedSteps'):
                    print(f"   └─ Estimated Steps: {section.get('estimatedSteps')}")
                
                print(f"   └─ Reasoning:")
                reasoning = section.get('reasoning', 'No reasoning provided')
                # Word wrap reasoning at 90 chars
                words = reasoning.split()
                line = "      "
                for word in words:
                    if len(line) + len(word) + 1 > 90:
                        print(line)
                        line = "      " + word
                    else:
                        line += (" " if line != "      " else "") + word
                if line != "      ":
                    print(line)
                
                if section.get('confidence'):
                    print(f"   └─ 🎯 Confidence: {section.get('confidence')}")
            
            # Validation Check
            print(f"\n{'─'*100}")
            print(f"🔍 VALIDATION CHECK")
            print(f"{'─'*100}")
            
            estimated = overall.get('totalEstimatedSteps', 0)
            actual_known = 37  # We know from manual count
            
            print(f"   Expected Steps (manual count): ~37")
            print(f"   AI Estimated Steps: {estimated}")
            
            if estimated >= 35 and estimated <= 45:
                print(f"   ✅ EXCELLENT - AI estimate within 20% of actual")
            elif estimated >= 30 and estimated <= 50:
                print(f"   ⚠️  GOOD - AI estimate within reasonable range")
            else:
                print(f"   ❌ NEEDS IMPROVEMENT - AI estimate significantly off")
            
            print(f"\n{'='*100}")
            print(f"  ✅ STAGE 0 TEST COMPLETE")
            print(f"{'='*100}\n")
            
            return data
            
        else:
            print(f"\n❌ ANALYSIS FAILED")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"\n❌ TEST FAILED")
        print(f"   Error: {e}")
        return None

def test_full_pipeline(analysis):
    """Test the complete pipeline with full document"""
    if not analysis:
        print("⚠️  Cannot test full pipeline without analysis")
        return
    
    print_header("FULL PIPELINE TEST: Stages 1-3 (Flowchart Generation)")
    
    # Auto-approve flowchartable sections
    approved_sections = [
        sec['sectionId'] for sec in analysis.get('sections', [])
        if sec.get('classification') == 'flowchartable'
    ]
    
    if not approved_sections:
        print("❌ No flowchartable sections found")
        return
    
    print(f"🎯 Approved {len(approved_sections)} flowchartable sections")
    print(f"🔄 Generating flowchart...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/process/generate-from-analysis",
            json={
                "documentText": FULL_BCP_TEXT,
                "analysisId": analysis['analysisId'],
                "approvedSections": approved_sections,
                "userCorrections": []
            },
            timeout=180
        )
        
        elapsed = time.time() - start_time
        print(f"⏱️  Generation Time: {elapsed:.1f} seconds")
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ FLOWCHART GENERATED SUCCESSFULLY!")
            
            processes = data.get('processes', [])
            if processes:
                process = processes[0]
                
                print(f"\n{'─'*100}")
                print(f"📊 FLOWCHART STRUCTURE")
                print(f"{'─'*100}")
                print(f"   Process Name: {process.get('processName')}")
                print(f"   Description: {process.get('description', 'N/A')[:100]}...")
                print(f"   Total Nodes: {len(process.get('nodes', []))}")
                print(f"   Decision Nodes: {sum(1 for n in process.get('nodes', []) if n.get('type') == 'decision')}")
                print(f"   Swim Lanes: {len(process.get('swimLanes', []))}")
                print(f"   Edges (Connections): {len(process.get('edges', []))}")
                print(f"   Actors: {', '.join(process.get('actors', [])[:5])}")
                
                # Show swim lanes if any
                if process.get('swimLanes'):
                    print(f"\n   🏊 Swim Lanes Detected:")
                    for lane in process.get('swimLanes', []):
                        print(f"      • {lane.get('name')}: {lane.get('role', 'N/A')}")
                
                # Show sample nodes
                print(f"\n   📋 Sample Nodes (first 5):")
                for i, node in enumerate(process.get('nodes', [])[:5], 1):
                    node_type = node.get('type', 'unknown')
                    icon = {'trigger': '▶️', 'decision': '◆', 'active': '▪️', 'warning': '⚠️'}.get(node_type, '•')
                    print(f"      {icon} {node.get('title', 'Untitled')}")
            
            # Coverage Report
            coverage = data.get('coverageReport', {})
            if coverage:
                print(f"\n{'─'*100}")
                print(f"📊 COVERAGE REPORT (Transparency)")
                print(f"{'─'*100}")
                
                completeness = coverage.get('completeness', 0)
                print(f"   Completeness: {completeness}%")
                print(f"   Steps Captured: {coverage.get('stepsCaptured')}/{coverage.get('stepsExpected')}")
                print(f"   Nodes with Operational Details: {coverage.get('nodesWithOperationalDetails', 0)}")
                print(f"   Decision Nodes Mapped: {coverage.get('decisionNodesMapped', 0)}")
                print(f"   Swim Lanes: {coverage.get('swimLanes', 0)}")
                
                # Status indicator
                if completeness >= 90:
                    print(f"\n   ✅ EXCELLENT COVERAGE")
                elif completeness >= 70:
                    print(f"\n   ⚠️  GOOD COVERAGE")
                else:
                    print(f"\n   ❌ INCOMPLETE - NEEDS REVIEW")
                
                # Exclusions
                exclusions = coverage.get('exclusions', [])
                if exclusions:
                    print(f"\n   ℹ️  Excluded Sections ({len(exclusions)}):")
                    for exc in exclusions[:3]:
                        print(f"      • {exc.get('section')}")
                        print(f"        Reason: {exc.get('reasoning', 'N/A')[:80]}...")
            
            print(f"\n{'='*100}")
            print(f"  🎉 FULL PIPELINE TEST COMPLETE!")
            print(f"{'='*100}\n")
            
        else:
            print(f"\n❌ FLOWCHART GENERATION FAILED")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text[:500]}")
    
    except Exception as e:
        print(f"\n❌ TEST FAILED")
        print(f"   Error: {e}")

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                  ║
║                    SUPERINTELLIGENT AI - FULL BCP SOP DOCUMENT TEST                             ║
║                                                                                                  ║
║  Testing with the complete BCP SOP #8 - Wilsar Outage document                                 ║
║  Expected: ~37 procedural steps across multiple decision trees                                  ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Stage 0: Document Analysis
    analysis = test_stage_0_full_document()
    
    if analysis:
        print("\n⏸️  Proceeding to full flowchart generation (Stages 1-3)...\n")
        
        # Stages 1-3: Full Pipeline
        test_full_pipeline(analysis)
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                  ║
║                                  🎉 TESTING COMPLETE 🎉                                         ║
║                                                                                                  ║
║  Review the results above to see if the superintelligent AI:                                    ║
║  ✅ Correctly identified all sections (flowchartable vs reference)                              ║
║  ✅ Estimated the correct number of steps (~37)                                                 ║
║  ✅ Provided clear reasoning for classifications                                                 ║
║  ✅ Generated a complete flowchart with all decision points                                      ║
║  ✅ Captured operational details (contacts, systems, templates)                                  ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    main()
