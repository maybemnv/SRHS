import re
from typing import List, Dict, Any

def process_chatbot_query(query: str, patients_data: List[Dict[str, Any]]) -> str:
    """
    Process chatbot queries and return filtered patient information.
    Basic keyword-based NLP implementation.
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
        return handle_general_query(query, patients_data, patient_id, disease_keywords)

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
