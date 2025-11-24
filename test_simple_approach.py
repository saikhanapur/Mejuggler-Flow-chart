import requests
import json
import time

BACKEND_URL = "https://smartsop.preview.emergentagent.com"

BCP_TEXT = open('/app/test_full_bcp_document.py').read().split('FULL_BCP_TEXT = """')[1].split('"""')[0]

print("🚀 Testing SIMPLE ONE-SHOT Approach")
print("="*80)

start = time.time()

response = requests.post(
    f"{BACKEND_URL}/api/process/simple-generate",
    json={"text": BCP_TEXT, "inputType": "document"},
    timeout=60
)

elapsed = time.time() - start

print(f"⏱️  Time: {elapsed:.1f} seconds")
print(f"📡 Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    process = data['processes'][0]
    print(f"\n✅ SUCCESS!")
    print(f"   Nodes: {len(process['nodes'])}")
    print(f"   Edges: {len(process['edges'])}")
    print(f"   Swim Lanes: {len(process.get('swimLanes', []))}")
    
    # Check for rich details
    nodes_with_purpose = sum(1 for n in process['nodes'] if n.get('operationalDetails', {}).get('purpose'))
    print(f"   Nodes with PURPOSE: {nodes_with_purpose}/{len(process['nodes'])}")
    
    # Show sample node
    if process['nodes']:
        sample = process['nodes'][0]
        print(f"\n📋 Sample Node:")
        print(f"   Title: {sample.get('title')}")
        print(f"   Type: {sample.get('type')}")
        details = sample.get('operationalDetails', {})
        if details.get('purpose'):
            print(f"   Purpose: {details['purpose'][:80]}...")
else:
    print(f"❌ Failed: {response.text[:500]}")
