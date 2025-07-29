import re
from typing import List, Dict, Any
import os
import google.generativeai as genai
import requests
from dotenv import load_dotenv

load_dotenv()

def process_chatbot_query(query: str, data: List[Dict[str, Any]], role: str) -> str:
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
    
    # Role-specific logic
    if role == 'doctor':
        if 'show' in query or 'find' in query or 'list' in query:
            return handle_search_query(query, data, patient_id, disease_keywords)
        elif 'count' in query or 'how many' in query or 'total' in query:
            return handle_count_query(query, data, disease_keywords)
        elif 'help' in query or 'commands' in query:
            return get_help_message('doctor')
        else:
            return call_groq_llama3(query, role='doctor')
    
    elif role == 'patient':
        if not data:
            return "Could not retrieve your data. Please try again later."
        
        patient_data = data[0]  # Patient data is the first element
        
        if any(word in query for word in ['help', 'commands', 'options']):
            return get_help_message('patient')
        elif any(word in query for word in ['my reports', 'my records']):
            return handle_patient_reports_query(patient_data)
        elif any(word in query for word in ['which doctors', 'who has access']):
            return handle_patient_access_query(patient_data)
        else:
            return call_groq_llama3(query, role='patient')
    
    return "Invalid role specified."

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

def get_help_message(role: str) -> str:
    """Return help message with available commands"""
    if role == 'doctor':
        return """🤖 Medical Assistant Commands:

📊 **Patient Search**:
• "Show all patients"
• "Find patient ID [number]"
• "Show patients with [disease]"

📈 **Statistics**:
• "How many patients?"
• "Count patients with [disease]"

💡 **Examples**:
• "Show patients with cancer"
• "Find patient ID 102"""
    
    elif role == 'patient':
        return """🤖 AI Assistant Commands:

📄 **My Records**:
• "Show my reports"
• "Summarize my recent reports"

🔑 **Access**:
• "Which doctors have access?"

💡 **Examples**:
• "When was my last report for diabetes?"
• "Show my reports from the last month"""


def call_groq_llama3(prompt: str, role: str) -> str:
    """Call Groq Cloud Llama 3-70B for generative medical chatbot answers."""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return "[Error: GROQ_API_KEY not set in environment.]"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    if role == 'doctor':
        system_prompt = "You are a helpful medical assistant for a doctor. You are analyzing data from patients who have granted this doctor access. Be concise and professional. Always remind users to consult a real doctor for definitive medical advice."
    else: # Patient
        system_prompt = "You are a helpful AI assistant for a patient viewing their own health records. Be supportive and clear. Always strongly remind them that you are an AI and they must consult their real doctor for any medical advice."

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
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

def handle_patient_reports_query(patient_data: Dict[str, Any]) -> str:
    """Handle queries about a patient's own reports."""
    reports = patient_data.get('reports', [])
    if not reports:
        return "You have no medical reports uploaded yet."
    
    result = f"You have {len(reports)} medical reports:\n"
    for r in sorted(reports, key=lambda x: x.upload_date, reverse=True)[:5]:
        result += f"• **{r.disease_name}** - {r.upload_date.strftime('%B %d, %Y')}\n"
    
    if len(reports) > 5:
        result += f"...and {len(reports) - 5} more."
        
    return result

def handle_patient_access_query(patient_data: Dict[str, Any]) -> str:
    """Handle queries about which doctors have access."""
    # This assumes 'granted_accesses' is passed in the patient_data dict.
    # The route currently doesn't provide this, so this is a placeholder.
    # For now, we can't answer this question from the patient side.
    return "I'm sorry, I can't check which doctors have access right now. You can see the list of doctors on your dashboard."
