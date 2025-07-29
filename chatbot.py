import re
from typing import List, Dict, Any
import os
import google.generativeai as genai
import requests
from dotenv import load_dotenv

load_dotenv()

def process_chatbot_query(query: str, patients_data: List[Dict[str, Any]]) -> str:
    """
    Process chatbot queries and return filtered patient information.
    Basic keyword-based NLP implementation, with Gemini fallback for open-ended queries.
    """
    query = query.lower().strip()
    
    # Extract patient ID if mentioned
    patient_id_match = re.search(r'\b(?:patient\s+)?(?:id\s+)?(\d+)\b', query)
    patient_id = int(patient_id_match.group(1)) if patient_id_match else None
    
    # Extract disease names
    disease_keywords = []
    common_diseases = [
        'cancer', 'diabetes', 'hypertension', 'heart', 'lung', 'kidney',
        'liver', 'brain', 'blood', 'infection', 'fever', 'flu', 'covid',
        'pneumonia', 'asthma', 'arthritis', 'depression', 'anxiety'
    ]
    
    for disease in common_diseases:
        if disease in query:
            disease_keywords.append(disease)
    
    # Process different types of queries
    if 'show' in query or 'find' in query or 'list' in query:
        return handle_search_query(query, patients_data, patient_id, disease_keywords)
    elif 'count' in query or 'how many' in query or 'total' in query:
        return handle_count_query(query, patients_data, disease_keywords)
    elif 'help' in query or 'commands' in query:
        return get_help_message()
    else:
        # Try the old fallback first
        fallback = handle_general_query(query, patients_data, patient_id, disease_keywords)
        # If fallback is generic, use Gemini
        if fallback.startswith("I can help you"):
            llm_response = call_groq_llama3(query)
            return llm_response
        else:
            return fallback

def handle_search_query(query: str, patients_data: List[Dict[str, Any]], 
                       patient_id: int = None, disease_keywords: List[str] = None) -> str:
    """Handle search/filter queries"""
    
    if patient_id:
        # Search by patient ID
        matching_patients = [
            p for p in patients_data 
            if p['patient'].id == patient_id
        ]
        
        if matching_patients:
            patient = matching_patients[0]['patient']
            reports = matching_patients[0]['reports']
            return f"Found Patient ID {patient.id}: {patient.full_name}\n" \
                   f"Reports: {len(reports)} medical reports\n" \
                   f"Diseases: {', '.join(set(r.disease_name for r in reports))}"
        else:
            return f"No patient found with ID {patient_id}"
    
    elif disease_keywords:
        # Search by disease
        matching_patients = []
        for patient_data in patients_data:
            patient_diseases = [r.disease_name.lower() for r in patient_data['reports']]
            if any(keyword in ' '.join(patient_diseases) for keyword in disease_keywords):
                matching_patients.append(patient_data)
        
        if matching_patients:
            result = f"Found {len(matching_patients)} patients with {', '.join(disease_keywords)}:\n\n"
            for patient_data in matching_patients[:5]:  # Limit to 5 results
                patient = patient_data['patient']
                relevant_reports = [
                    r for r in patient_data['reports']
                    if any(keyword in r.disease_name.lower() for keyword in disease_keywords)
                ]
                result += f"• Patient ID {patient.id}: {patient.full_name}\n"
                result += f"  Relevant reports: {len(relevant_reports)}\n"
                if relevant_reports:
                    result += f"  Diseases: {', '.join(r.disease_name for r in relevant_reports)}\n"
                result += "\n"
            
            if len(matching_patients) > 5:
                result += f"... and {len(matching_patients) - 5} more patients"
            
            return result
        else:
            return f"No patients found with {', '.join(disease_keywords)}"
    
    else:
        # General patient list
        if not patients_data:
            return "No patients have granted you access yet."
        
        result = f"You have access to {len(patients_data)} patients:\n\n"
        for patient_data in patients_data:
            patient = patient_data['patient']
            reports = patient_data['reports']
            diseases = list(set(r.disease_name for r in reports))
            
            result += f"• Patient ID {patient.id}: {patient.full_name}\n"
            result += f"  Reports: {len(reports)}\n"
            if diseases:
                result += f"  Diseases: {', '.join(diseases[:3])}"
                if len(diseases) > 3:
                    result += f" and {len(diseases) - 3} more"
            result += "\n\n"
        
        return result

def handle_count_query(query: str, patients_data: List[Dict[str, Any]], 
                      disease_keywords: List[str] = None) -> str:
    """Handle counting queries"""
    
    if disease_keywords:
        # Count patients with specific diseases
        count = 0
        for patient_data in patients_data:
            patient_diseases = [r.disease_name.lower() for r in patient_data['reports']]
            if any(keyword in ' '.join(patient_diseases) for keyword in disease_keywords):
                count += 1
        
        return f"You have {count} patients with {', '.join(disease_keywords)}"
    
    else:
        # Total patient count
        total_patients = len(patients_data)
        total_reports = sum(len(p['reports']) for p in patients_data)
        
        # Disease distribution
        disease_counts = {}
        for patient_data in patients_data:
            for report in patient_data['reports']:
                disease = report.disease_name
                disease_counts[disease] = disease_counts.get(disease, 0) + 1
        
        result = f"Total Statistics:\n"
        result += f"• Patients: {total_patients}\n"
        result += f"• Total Reports: {total_reports}\n"
        
        if disease_counts:
            result += f"• Top Diseases:\n"
            sorted_diseases = sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)
            for disease, count in sorted_diseases[:5]:
                result += f"  - {disease}: {count} cases\n"
        
        return result

def handle_general_query(query: str, patients_data: List[Dict[str, Any]], 
                        patient_id: int = None, disease_keywords: List[str] = None) -> str:
    """Handle general queries that don't fit other categories"""
    
    if patient_id or disease_keywords:
        return handle_search_query(query, patients_data, patient_id, disease_keywords)
    
    # Default response with suggestions
    return "I can help you find patients and analyze medical data. Try asking:\n\n" \
           "• 'Show all patients'\n" \
           "• 'Find patient ID 123'\n" \
           "• 'Show patients with cancer'\n" \
           "• 'How many patients do I have?'\n" \
           "• 'Count patients with diabetes'\n\n" \
           "What would you like to know?"

def get_help_message() -> str:
    """Return help message with available commands"""
    return """🤖 Medical Assistant Chatbot Commands:

📊 Patient Search:
• "Show all patients" - List all accessible patients
• "Find patient ID [number]" - Find specific patient
• "Show patients with [disease]" - Filter by disease

📈 Statistics:
• "How many patients?" - Total patient count
• "Count patients with [disease]" - Disease-specific count
• "Total reports" - Overall statistics

💡 Examples:
• "Show patients with cancer"
• "Find patient ID 102"
• "How many patients with diabetes?"
• "List all patients"

Just type your question naturally!"""


def call_groq_llama3(prompt: str) -> str:
    """Call Groq Cloud Llama 3-70B for generative medical chatbot answers."""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return "[Error: GROQ_API_KEY not set in environment.]"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful medical assistant. Always remind users to consult a real doctor for medical advice."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 512,
        "temperature": 0.2
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[Groq LLM Error: {e}]"

def process_patient_chatbot_query(query: str, patient_data: dict) -> str:
    """
    Process patient chatbot queries: contact doctors, request/access reports, list granted accesses, and LLM fallback.
    """
    query = query.lower().strip()
    patient = patient_data['patient']
    reports = patient_data['reports']
    granted_accesses = patient_data['granted_accesses']

    # Help/commands prompt
    if any(word in query for word in ['help', 'commands', 'what can you do', 'options', 'examples']):
        help_message = (
            "🤖 Patient Chatbot Commands:\n\n"
            "📄 Medical Records:\n"
            "• 'Show my reports' - List your uploaded medical reports\n"
            "• 'Which doctors have access?' - List doctors with access to your records\n"
            "• 'Contact my doctor' - See which doctors you can contact\n"
            "\n💡 Examples:\n"
            "• 'Show my reports'\n"
            "  → You have X medical reports. • Disease1 (2024-01-01) ...\n"
            "• 'Which doctors have access?'\n"
            "  → Doctors with access to your records: Dr. Smith (smith@email.com) ...\n"
            "• 'Contact my doctor'\n"
            "  → You can contact your doctors: Dr. Smith. (Messaging feature coming soon.)\n"
            "\nJust type your question naturally!"
        )
        return help_message

    if any(word in query for word in ['contact doctor', 'message doctor', 'talk to doctor', 'reach doctor']):
        # Placeholder for contacting doctor
        if granted_accesses:
            doctor_names = ', '.join([doctor.full_name for _, doctor in granted_accesses])
            return f"You can contact your doctors: {doctor_names}. (Messaging feature coming soon.)"
        else:
            return "You have not granted access to any doctors yet."

    if any(word in query for word in ['my reports', 'my records', 'show reports', 'show records', 'access reports', 'access records']):
        if not reports:
            return "You have no medical reports uploaded yet."
        result = f"You have {len(reports)} medical reports.\n"
        for r in reports[:5]:
            result += f"• {r.disease_name} ({r.upload_date.strftime('%Y-%m-%d')})\n"
        if len(reports) > 5:
            result += f"...and {len(reports) - 5} more."
        return result

    if any(word in query for word in ['which doctors', 'who has access', 'granted access', 'doctor access']):
        if not granted_accesses:
            return "No doctors currently have access to your records."
        result = "Doctors with access to your records:\n"
        for _, doctor in granted_accesses:
            result += f"• Dr. {doctor.full_name} ({doctor.email})\n"
        return result

    # LLM fallback for open-ended queries
    llm_response = call_groq_llama3(
        f"[Patient prompt] {query}\n(You are a helpful assistant for patients. Always remind users to consult their doctor for medical advice.)"
    )
    return llm_response
