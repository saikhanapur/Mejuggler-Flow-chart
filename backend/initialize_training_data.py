"""
Initialize training database with example documents.
Run this script to populate the learning system with initial examples.
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from learning_system import LearningSystem
import PyPDF2

async def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"❌ Failed to extract {pdf_path}: {e}")
        return ""


async def initialize_training_data():
    """Initialize the learning system with training examples."""
    
    # Connect to MongoDB
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    
    learning_system = LearningSystem(client)
    
    print("🎓 Initializing AI Training Database...")
    print("=" * 60)
    
    # Training Example 1: Welfare First Fatigue Alert (SINGLE PROCESS)
    print("\n📄 Example 1: Welfare First Fatigue Alert SOP")
    welfare_text = await extract_pdf_text("/tmp/welfare_fatigue.pdf")
    if welfare_text:
        example_id = await learning_system.store_training_example(
            document_text=welfare_text,
            document_name="Welfare First Fatigue Alert SOP",
            user_classification={
                "multipleProcesses": False,
                "processCount": 1,
                "document_type": "Emergency SOP",
                "reasoning": "Single 5-step sequential process for handling fatigue alerts. Steps are consecutive phases of ONE workflow, not separate processes."
            },
            preferred_structure={
                "node_count": "8-12",
                "grouping_strategy": "Group similar actions (e.g., verify alert steps into one node)",
                "decision_points": "Clear decision after verification (Genuine vs False Positive)",
                "key_insight": "Escalation steps should be grouped, not separate nodes"
            },
            industry="Emergency Services",
            user_id="admin"
        )
        print(f"✅ Stored: {example_id}")
    
    # Training Example 2: BCP RingCentral Outage (SINGLE PROCESS with parallel tasks)
    print("\n📄 Example 2: BCP RingCentral Outage")
    ringcentral_text = await extract_pdf_text("/tmp/bcp_ringcentral.pdf")
    if ringcentral_text:
        example_id = await learning_system.store_training_example(
            document_text=ringcentral_text,
            document_name="BCP RingCentral Outage ALL v1.3",
            user_classification={
                "multipleProcesses": False,
                "processCount": 1,
                "document_type": "Business Continuity Plan",
                "reasoning": "Single BCP with parallel onshore/offshore tasks. Parallel execution does NOT mean multiple processes - it's one coordinated response with different teams.",
                "has_existing_flowchart": True
            },
            preferred_structure={
                "node_count": "10-15",
                "grouping_strategy": "Use swim lanes for Onshore/Offshore teams",
                "decision_points": "Outage confirmed decision, then parallel execution",
                "key_insight": "Parallel tasks = swim lanes, NOT separate processes"
            },
            industry="Physical Security Services",
            user_id="admin"
        )
        print(f"✅ Stored: {example_id}")
    
    # Training Example 3: Fleet Vehicle Breakdown (SINGLE PROCESS with decision branches)
    print("\n📄 Example 3: Fleet Vehicle Breakdown Procedure")
    fleet_text = await extract_pdf_text("/tmp/fleet_vehicle.pdf")
    if fleet_text:
        example_id = await learning_system.store_training_example(
            document_text=fleet_text,
            document_name="Fleet Vehicle Breakdown Procedure v2.1",
            user_classification={
                "multipleProcesses": False,
                "processCount": 1,
                "document_type": "Operational Procedure",
                "reasoning": "Single process with decision branches (answered vs not answered). Decision branches are part of ONE process flow, not separate processes.",
                "has_existing_flowchart": True
            },
            preferred_structure={
                "node_count": "8-10",
                "grouping_strategy": "Group information gathering steps",
                "decision_points": "Two main decisions: Custom Fleet answered? Manager answered?",
                "key_insight": "Alternative pathways are branches, not separate processes"
            },
            industry="Physical Security Services",
            user_id="admin"
        )
        print(f"✅ Stored: {example_id}")
    
    # COUNTER-EXAMPLE: What WOULD be multiple processes
    print("\n📄 Counter-Example: What WOULD constitute multiple processes")
    counter_example_text = """
    HR Handbook - Multiple Processes Example
    
    Process 1: Employee Onboarding
    - Steps: Application review, offer letter, background check, orientation
    
    Process 2: Performance Review
    - Steps: Goal setting, mid-year review, annual review, rating
    
    Process 3: Employee Termination
    - Steps: Documentation, exit interview, final paycheck, equipment return
    
    These are THREE SEPARATE, INDEPENDENT processes with different triggers, steps, and outcomes.
    """
    
    example_id = await learning_system.store_training_example(
        document_text=counter_example_text,
        document_name="HR Handbook (Hypothetical Multi-Process Example)",
        user_classification={
            "multipleProcesses": True,
            "processCount": 3,
            "processTitles": ["Employee Onboarding", "Performance Review", "Employee Termination"],
            "document_type": "Policy Handbook",
            "reasoning": "Three COMPLETELY INDEPENDENT processes with different: triggers, steps, participants, and outcomes. Each can run without the others."
        },
        preferred_structure={
            "node_count_per_process": "6-10",
            "grouping_strategy": "Each process is separate flowchart",
            "key_insight": "TRUE multi-process = independent workflows that don't depend on each other"
        },
        industry="Human Resources",
        user_id="admin"
    )
    print(f"✅ Stored: {example_id}")
    
    print("\n" + "=" * 60)
    print("✅ Training database initialized successfully!")
    print("\nNext: The AI will use these examples for few-shot learning.")
    print("      Encourage users to provide feedback to improve accuracy.")

if __name__ == "__main__":
    asyncio.run(initialize_training_data())
