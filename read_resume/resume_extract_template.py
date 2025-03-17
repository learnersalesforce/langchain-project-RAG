import fitz  # PyMuPDF for handling PDFs
import os
import re
import spacy
from docx import Document

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# ✅ Extract text from PDF resumes
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        return "\n".join([page.get_text("text") for page in doc]).strip()
    except Exception as e:
        print(f"❌ Error extracting text from PDF {pdf_path}: {e}")
        return ""

# ✅ Extract text from DOCX resumes
def extract_text_from_docx(docx_path):
    try:
        doc = Document(docx_path)
        return "\n".join([para.text for para in doc.paragraphs]).strip()
    except Exception as e:
        print(f"❌ Error extracting text from DOCX {docx_path}: {e}")
        return ""

# ✅ Extract resume information using NLP & regex
def extract_information(text):
    doc = nlp(text)

    # Extract Name
    name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), "Unknown")

    # Extract Email, Phone, LinkedIn
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone_match = re.search(r"\+?\d[\d\s\-()]{8,}\d", text)
    linkedin_match = re.search(r"(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9-]+", text)

    # Extract Personal Details
    father_match = re.search(r"Father(?:'s)? Name[:\-]?\s*(.*)", text, re.IGNORECASE)
    dob_match = re.search(r"Date of Birth[:\-]?\s*(.*)", text, re.IGNORECASE)
    address_match = re.search(r"Current Address[:\-]?\s*(.*)", text, re.IGNORECASE)
    languages_match = re.search(r"Languages[:\-]?\s*(.*)", text, re.IGNORECASE)

    # Extract Education
    education_matches = re.findall(
        r"((?:Bachelor|Master|B\.Tech|M\.Tech|MBA|PhD|Graduate)[^,]*)\s*(?:from|at)?\s*([\w\s]+University|Institute)[,\s]*(?:CGPA[:\-]?\s*(\d+\.\d+)|Percentage[:\-]?\s*(\d+%))?",
        text, re.IGNORECASE
    )
    education = [f"{deg} from {uni} (CGPA: {cgpa})" if cgpa else f"{deg} from {uni}" for deg, uni, cgpa, _ in education_matches]

    # Extract Certifications
    certifications = re.findall(r"((?:Salesforce|AWS|Azure|Google Cloud|Microsoft)[\w\s]+Certified[\w\s]*)", text, re.IGNORECASE)

    # Extract Technical Skills
    skills = re.findall(r"(JavaScript|Python|Java|C\+\+|C#|SQL|MySQL|MongoDB|Apex|SOQL|LWC|Salesforce|MuleSoft|Docker|Kubernetes)", text, re.IGNORECASE)

    # Extract Projects
    project_matches = re.findall(r"(?i)Projects?\s*[:\-]?\s*(.*?)\n", text)
    url_matches = re.findall(r"https?://[^\s]+", text)
    projects = [f"{proj} ({url})" for proj, url in zip(project_matches, url_matches)]

    # Extract Experience
    experience_matches = re.findall(r"(\w[\w\s,.-]+)\s(at|with|in)\s([\w\s]+)\s\(?(\d{4})?", text, re.IGNORECASE)
    experience = [f"{role} at {company} ({year})" if year else f"{role} at {company}" for role, _, company, year in experience_matches]

    return {
        "Name": name,
        "Email": email_match.group() if email_match else "Not Found",
        "Phone": phone_match.group() if phone_match else "Not Found",
        "LinkedIn": linkedin_match.group() if linkedin_match else "Not Found",
        "Father Name": father_match.group(1).strip() if father_match else "Not Found",
        "Date of Birth": dob_match.group(1).strip() if dob_match else "Not Found",
        "Address": address_match.group(1).strip() if address_match else "Not Found",
        "Languages": languages_match.group(1).strip() if languages_match else "Not Found",
        "Education": ", ".join(education) if education else "Not Available",
        "Certifications": ", ".join(certifications) if certifications else "Not Available",
        "Technical Skills": ", ".join(set(skills)) if skills else "Not Available",
        "Projects": ", ".join(projects) if projects else "Not Available",
        "Experience": ", ".join(experience) if experience else "Not Available",
    }

# ✅ Insert extracted data into template.pdf (Table Format)
def fill_template_with_table(data, template_path, output_folder):
    doc = fitz.open(template_path)

    output_filename = f"{data['Name'].replace(' ', '_')}_Resume.pdf"
    output_path = os.path.join(output_folder, output_filename)

    if len(doc) == 0:
        doc.insert_page(0)

    # ✅ Define starting position (Adjust for formatting)
    x, y = 50, 100
    line_spacing = 15

    # ✅ Insert table headers
    headers = ["Field", "Value"]
    doc[0].insert_text((x, y), f"{headers[0]:<20} {headers[1]:<60}", fontsize=12, color=(0, 0, 0))
    y += line_spacing

    # ✅ Insert extracted resume data into table format
    for key, value in data.items():
        doc[0].insert_text((x, y), f"{key:<20}: {value}", fontsize=11, color=(0, 0, 0))
        y += line_spacing

    doc.save(output_path)
    doc.close()
    print(f"✅ Successfully saved: {output_path}")

# ✅ Process resumes and insert extracted data into the template
def process_resumes(resume_folder, template_pdf, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in os.listdir(resume_folder):
        if file.lower().endswith((".pdf", ".docx")):
            file_path = os.path.join(resume_folder, file)
            print(f"\n🚀 Processing: {file_path}")

            text = extract_text_from_pdf(file_path) if file.endswith(".pdf") else extract_text_from_docx(file_path)
            if not text.strip():
                print(f"❌ No text extracted from {file_path}")
                continue

            extracted_info = extract_information(text)
            fill_template_with_table(extracted_info, template_pdf, output_folder)

# ✅ Run the script
if __name__ == "__main__":
    resumes_folder = "D:/Updated-Langchain/read_resume"
    template_pdf = "D:/Updated-Langchain/read_resume/template.pdf"
    output_dir = "D:/Updated-Langchain/read_resume/filled_pdfs"

    process_resumes(resumes_folder, template_pdf, output_dir)
