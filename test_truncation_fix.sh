#!/bin/bash

echo "========================================="
echo "TESTING TRUNCATION FIX"
echo "========================================="

# Test document - generate a large document
cat > /tmp/large_test_document.txt << 'EOF'
BUSINESS CONTINUITY PLAN - IT DISASTER RECOVERY

PART 1: DETECTION & INITIAL RESPONSE (Pages 1-10)
Step 1: Security team receives automated alert from monitoring system
Step 2: Security analyst verifies alert authenticity
Step 3: Log incident in ServiceNow with severity assessment
Step 4: Check if production systems affected
Step 5: If production: escalate to Incident Commander
Step 6: If non-production: continue monitoring
Step 7: Incident Commander assembles response team
Step 8: Notify CTO via phone
Step 9: Notify Legal team
Step 10: Notify PR team

PART 2: TECHNICAL ASSESSMENT (Pages 11-20)
Step 11: System admin checks server health dashboard
Step 12: Review error logs for root cause indicators
Step 13: Network team checks firewall rules
Step 14: Network team verifies VPN connectivity
Step 15: Database team checks database integrity
Step 16: Run backup verification scripts
Step 17: If database corrupted: initiate restore from backup
Step 18: If database intact: continue investigation
Step 19: Review recent code deployments
Step 20: Check configuration management for recent changes

PART 3: ROOT CAUSE ANALYSIS (Pages 21-30)
Step 21: Identify primary failure point
Step 22: Document timeline of events
Step 23: Interview on-call engineers
Step 24: Review change logs
Step 25: Check for security incidents
Step 26: Analyze performance metrics
Step 27: Create detailed incident report
Step 28: Determine business impact
Step 29: Calculate downtime costs
Step 30: Document affected services

PART 4: FIX DEVELOPMENT (Pages 31-40)
Step 31: Create fix plan with rollback strategy
Step 32: Get approval from Incident Commander
Step 33: If high-risk: wait for change advisory board approval
Step 34: If low-risk: proceed with fix development
Step 35: Deploy fix to development environment
Step 36: Run automated test suite
Step 37: Deploy to staging environment
Step 38: Conduct user acceptance testing
Step 39: If tests fail: rollback and revise
Step 40: If tests pass: schedule production deployment

PART 5: PRODUCTION DEPLOYMENT (Pages 41-50)
Step 41: Create deployment checklist
Step 42: Notify all stakeholders of deployment window
Step 43: Deploy fix to production during maintenance window
Step 44: Monitor production logs in real-time
Step 45: Run smoke tests
Step 46: Verify issue is resolved
Step 47: Update ServiceNow ticket with resolution
Step 48: Notify stakeholders of resolution

PART 6: POST-INCIDENT REVIEW & RECOVERY (Pages 51-60)
Step 49: Conduct post-incident review within 48 hours
Step 50: Document lessons learned
Step 51: Update runbooks based on findings
Step 52: Implement preventive measures
Step 53: Update disaster recovery plan
Step 54: Train team on new procedures
Step 55: Close incident ticket
Step 56: Archive incident documentation

CONTACT DIRECTORY:
- CTO: John Smith - 555-0100
- IT Manager: Jane Doe - 555-0200
- Security Team: security@company.com
- Database Admin: db-admin@company.com
- Network Team: network@company.com

SYSTEM DETAILS:
- Monitoring: Datadog (https://app.datadoghq.com)
- Ticketing: ServiceNow (https://company.service-now.com)
- Code Repository: GitHub (https://github.com/company)
- CI/CD: Jenkins (https://jenkins.company.com)

TEMPLATES:
- Incident Notification Email
- Stakeholder Update Template
- Post-Incident Review Template
- Lessons Learned Document

This document is approximately 60 pages in printed form.
Character count should be around 4000+ characters.
EOF

DOC_TEXT=$(cat /tmp/large_test_document.txt)
DOC_LENGTH=${#DOC_TEXT}

echo ""
echo "Test Document Stats:"
echo "- Character count: $DOC_LENGTH"
echo "- Estimated pages: ~$(($DOC_LENGTH / 800))"
echo ""

# Test OLD service (with rollback code)
echo "========================================="
echo "TESTING: OLD SERVICE (EROAD)"
echo "========================================="

timeout 120 curl -s -X POST "https://sop-transformer.preview.emergentagent.com/api/process/eroad-style" \
  -H "Content-Type: application/json" \
  -d "{\"text\": $(echo "$DOC_TEXT" | jq -Rs .), \"inputType\": \"document\"}" 2>&1 | python3 << 'PYEOF'
import sys, json
try:
    data = json.load(sys.stdin)
    if 'processes' in data and len(data['processes']) > 0:
        proc = data['processes'][0]
        nodes = proc.get('nodes', [])
        print(f"✅ OLD Service Result:")
        print(f"   Nodes extracted: {len(nodes)}")
        print(f"   First 3 nodes:")
        for i, node in enumerate(nodes[:3], 1):
            print(f"     {i}. {node.get('title', 'N/A')}")
        print(f"   Last 3 nodes:")
        for i, node in enumerate(nodes[-3:], 1):
            print(f"     {i}. {node.get('title', 'N/A')}")
    else:
        print(f"❌ Error: {data.get('detail', 'Unknown error')}")
except Exception as e:
    print(f"❌ Error: {e}")
PYEOF

echo ""
echo "========================================="
echo "EXPECTED: Should see steps from BOTH"
echo "          beginning AND end of document"
echo "========================================="
