#!/usr/bin/env python3
"""
Test only the EROAD-style flowchart generation endpoint
"""

import requests
import json
import sys

# Configuration
BASE_URL = "https://flowmapper-2.preview.emergentagent.com/api"
TIMEOUT = 120

def test_eroad_style_endpoint():
    """Test EROAD-style flowchart generation endpoint"""
    print("🎨 Testing EROAD-Style Flowchart Generation...")
    
    # Sample document from the review request
    sample_document = """Business Continuity Procedure: System Outage Response

1. Identify the outage - Check monitoring systems
2. Notify supervisor - Call on-duty manager immediately
3. Setup BCP tracking - Create incident timeline in system
4. Contact stakeholders - Email all affected teams
5. Begin manual operations - Switch to backup procedures
6. Monitor status - Check every 30 minutes for restoration
7. Test system - Verify services are operational
8. Notify restoration - Inform all parties systems are back
9. Resume normal operations - Return to standard workflows

Emergency Contacts:
- IT Support: 0800 123 456
- On-call Manager: 0800 789 012"""
    
    try:
        payload = {
            "text": sample_document,
            "inputType": "text"
        }
        
        print(f"📡 Making request to: {BASE_URL}/process/eroad-style")
        print(f"📄 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(f"{BASE_URL}/process/eroad-style", 
                               json=payload, 
                               headers={'Content-Type': 'application/json'},
                               timeout=TIMEOUT)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: Response received")
            print(f"📊 Response structure: {list(result.keys())}")
            
            if 'processes' in result:
                processes = result['processes']
                print(f"📈 Number of processes: {len(processes)}")
                
                if processes:
                    process = processes[0]
                    print(f"🔍 Process fields: {list(process.keys())}")
                    
                    nodes = process.get('nodes', [])
                    print(f"📍 Number of nodes: {len(nodes)}")
                    
                    if nodes:
                        print(f"🎯 Sample node structure: {list(nodes[0].keys())}")
                        print(f"📐 Node coordinates: x={nodes[0].get('x')}, y={nodes[0].get('y')}")
                        print(f"🏷️ Node status: {nodes[0].get('status')}")
                    
                    edges = process.get('edges', [])
                    print(f"🔗 Number of edges: {len(edges)}")
                    
                    quick_ref = process.get('quickReference', {})
                    print(f"⚡ Quick reference fields: {list(quick_ref.keys())}")
                    
                    progress_stages = process.get('progressStages', [])
                    print(f"📊 Progress stages: {len(progress_stages)}")
                    
                    swim_lanes = process.get('swimLanes', [])
                    print(f"🏊 Swim lanes: {len(swim_lanes)}")
                    
                    return True
            else:
                print(f"❌ FAIL: No 'processes' in response")
                print(f"📄 Full response: {json.dumps(result, indent=2)}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            print(f"📄 Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_eroad_style_endpoint()
    sys.exit(0 if success else 1)