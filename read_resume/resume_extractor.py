import fitz  # PyMuPDF for PDF processing
from docx import Document  # DOCX processing
import spacy  # NLP for entity recognition
import re  # Regex for pattern extraction
import os
import pandas as pd
import json

# Load NLP model
nlp = spacy.load("en_core_web_sm")

#  Extract Text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text("text") for page in doc])
        return text.strip()
    except Exception as e:
        print(f" Error extracting text from PDF {pdf_path}: {e}")
        return ""

#  Extract Text from DOCX
def extract_text_from_docx(docx_path):
    try:
        doc = Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f" Error extracting text from DOCX {docx_path}: {e}")
        return ""

#  Extract Certifications
def extract_certifications(text):
    certifications = re.findall(r"((?:Salesforce|AWS|Azure|Google Cloud|Microsoft)[\w\s]+Certified[\w\s]*)", text, re.IGNORECASE)
    return [cert.strip() for cert in certifications]

#  Extract Technical Skills
def extract_technical_skills(text):
    skills = re.findall(
        r"(JavaScript|Python|Java|C\+\+|C#|SQL|MySQL|PostgreSQL|MongoDB|Apex|SOQL|"
        r"SOSL|Visualforce|LWC|Aura|Salesforce|MuleSoft|REST API|SOAP API|GitHub|JIRA|"
        r"Data Loader|Lightning Web Components|Bitbucket|AWS|Azure|Google Cloud|Docker|Kubernetes)",
        text, re.IGNORECASE
    )
    return list(set([skill.strip() for skill in skills]))

#  Extract Projects and URLs
def extract_projects(text):
    projects = []
    
    # Extract project names
    project_matches = re.findall(r"(?i)Projects?\s*[:\-]?\s*(.*?)\n", text)

    # Extract URLs (if available)
    url_matches = re.findall(r"https?://[^\s]+", text)

    # Pair project names with URLs
    for i, project in enumerate(project_matches):
        project_name = project.strip()
        if len(project_name.split()) > 1:
            project_url = url_matches[i] if i < len(url_matches) else "Not Available"
            projects.append({"Project Name": project_name, "Project URL": project_url})

    return projects

#  Extract Education (Degree, University, CGPA, Percentage)
def extract_education(text):
    education = []
    education_matches = re.findall(
        r"((?:Bachelor|Master|B\.Tech|M\.Tech|MBA|PhD|Graduate)[^,]*)\s*(?:from|at)?\s*([\w\s]+University|Institute)[,\s]*(?:CGPA[:\-]?\s*(\d+\.\d+)|Percentage[:\-]?\s*(\d+%))?",
        text, re.IGNORECASE
    )

    for match in education_matches:
        degree, university, cgpa, percentage = match
        details = f"{degree} from {university}"
        if cgpa:
            details += f" (CGPA: {cgpa})"
        if percentage:
            details += f" (Percentage: {percentage})"
        education.append(details)

    return education

#  Extract Personal Details (Father Name, DOB, Address, Languages)
def extract_personal_details(text):
    details = {
        "Father Name": re.search(r"Father(?:'s)? Name[:\-]?\s*(.*)", text, re.IGNORECASE),
        "Date of Birth": re.search(r"Date of Birth[:\-]?\s*(.*)", text, re.IGNORECASE),
        "Address": re.search(r"Current Address[:\-]?\s*(.*)", text, re.IGNORECASE),
        "Languages": re.search(r"Languages[:\-]?\s*(.*)", text, re.IGNORECASE),
    }
    return {key: (match.group(1).strip() if match else "Not Found") for key, match in details.items()}

#  Extract Resume Information
def extract_information(text):
    doc = nlp(text)

    # Extract Key Information
    name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), "Unknown")
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone_match = re.search(r"\+?\d[\d\s\-()]{8,}\d", text)
    linkedin_match = re.search(r"(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9-]+", text)

    extracted_data = {
        "Name": name,
        "Email": email_match.group() if email_match else "Not Found",
        "Phone": phone_match.group() if phone_match else "Not Found",
        "LinkedIn": linkedin_match.group() if linkedin_match else "Not Found",
        **extract_personal_details(text),
        "Education": json.dumps(extract_education(text)),
        "Certifications": json.dumps(extract_certifications(text)),
        "Technical Skills": json.dumps(extract_technical_skills(text)),
        "Projects": json.dumps(extract_projects(text)),
    }

    return extracted_data

#  Process a Single Resume
def process_resume(file_path):
    ext = file_path.split(".")[-1].lower()
    text = extract_text_from_pdf(file_path) if ext == "pdf" else extract_text_from_docx(file_path)
    
    if not text.strip():
        print(f" Error: No text extracted from {file_path}")
        return None
    
    extracted_info = extract_information(text)
    extracted_info["Resume File"] = os.path.basename(file_path)
    
    return extracted_info

#  Process Multiple Resumes
def process_multiple_resumes(folder_path):
    if not os.path.exists(folder_path):
        print(f" Error: Folder path '{folder_path}' does not exist.")
        return []

    all_data = []
    for file in os.listdir(folder_path):
        if file.lower().endswith((".pdf", ".docx")):
            file_path = os.path.join(folder_path, file)
            print(f"\n Processing: {file_path}")
            data = process_resume(file_path)
            if data:
                all_data.append(data)

    if not all_data:
        print("⚠ Warning: No data extracted from resumes!")
    return all_data

#  Save Extracted Data to CSV (Name Based on First Resume)
def save_to_csv(data, folder_path):
    if not data:
        print(" No data to save!")
        return

    # Get the first valid name from the extracted resumes
    first_valid_name = next((d["Name"] for d in data if d["Name"] != "Unknown"), "Extracted_Resumes")
    
    # Generate CSV file using the extracted name
    csv_filename = f"{first_valid_name.replace(' ', '_')}-Resume.csv"
    csv_path = os.path.join(folder_path, csv_filename)
    
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig", quoting=1)
    
    print(f"\n Data saved to {csv_path}")

#  Run the Script
if __name__ == "__main__":
    folder_path = "D:/Updated-Langchain/read_resume"  # Change this path
    extracted_data = process_multiple_resumes(folder_path)
    
    if extracted_data:
        save_to_csv(extracted_data, folder_path)
