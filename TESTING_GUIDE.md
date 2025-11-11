# SUPERINTELLIGENT AI BACKEND - TESTING GUIDE

## Quick Test Commands

### 1. Test Stage 0: Document Analysis (the most important one!)

```bash
curl -X POST https://flowchart-genius-2.preview.emergentagent.com/api/process/analyze-document \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Business Continuity Procedure: System Outage\n\nStep 1: Identify the outage\nStep 2: Contact IT team\nStep 3: Notify stakeholders\n\nReferences:\n- IT Contact: John Doe (555-1234)\n- Escalation email template",
    "inputType": "document"
  }' | python -m json.tool
```

**What to expect:**
- Status 200
- JSON response with:
  - `analysisId`: UUID for this analysis
  - `documentSummary`: Brief description
  - `sections`: Array of classified sections with reasoning
  - `overallAnalysis`: Stats (estimated steps, complexity, etc.)

### 2. Test Learning System

```bash
curl https://flowchart-genius-2.preview.emergentagent.com/api/learning/insights | python -m json.tool
```

**What to expect:**
- Total analyses count
- Validation rate
- Top learned patterns

### 3. Test Full Pipeline (after getting analysisId from Step 1)

```bash
# Replace ANALYSIS_ID with the ID from step 1
curl -X POST https://flowchart-genius-2.preview.emergentagent.com/api/process/generate-from-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "documentText": "Business Continuity Procedure: System Outage\n\nStep 1: Identify the outage\nStep 2: Contact IT team\nStep 3: Notify stakeholders\n\nReferences:\n- IT Contact: John Doe (555-1234)\n- Escalation email template",
    "analysisId": "ANALYSIS_ID",
    "approvedSections": ["sec-1"],
    "userCorrections": []
  }' | python -m json.tool
```

**What to expect:**
- Status 200
- JSON with:
  - `processes`: Array with flowchart structure (nodes, edges, swimLanes)
  - `coverageReport`: Transparency report
  - Steps captured vs expected
  - Completeness percentage

## Using the Python Test Script

The comprehensive test script is located at `/app/test_superintelligent_backend.py`

Run it with:

```bash
cd /app
python test_superintelligent_backend.py
```

This will:
1. Test Stage 0 with BCP SOP sample
2. Check learning system
3. Test full pipeline (Stages 1-3)

## What's Working

✅ **Stage 0: Document Intelligence** - 100% working
- Classifies sections correctly
- Provides reasoning
- High confidence patterns
- Estimated 38-40 steps from your BCP SOP

✅ **Learning System** - 100% working  
- Stores analyses
- Tracks patterns
- Ready for user feedback

⚠️ **Stages 1-3** - In progress
- Structure extraction working
- JSON parsing being enhanced for complex documents
- May need prompt tuning for very large documents

## Next Steps

1. **Test Stage 0** - This is the most important! Run the curl command above
2. **Review the section classifications** - Does it make sense?
3. **Once satisfied**, we proceed to frontend UI

## Debugging

If you see errors, check backend logs:

```bash
tail -50 /var/log/supervisor/backend.err.log
```

Look for lines with:
- `🧠 Stage 0:` - Document analysis logs
- `🏗️ Stage 1:` - Structure extraction logs
- `❌` - Error indicators
