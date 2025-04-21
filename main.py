from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from dotenv import load_dotenv
from google.generativeai import types
from google import generativeai as genai
from langchain.prompts import PromptTemplate
import json

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Enable CORS if needed (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


llm = genai.GenerativeModel('gemini-1.5-flash', generation_config=types.GenerationConfig(
    max_output_tokens=1024, temperature=1,
))

# Define request model
class ResumeRequest(BaseModel):
    user_info: Dict
    job_description: str

# System prompt
SYSTEM_PROMPT = """You are an expert Resume Assistant specializing in crafting ATS-optimized resume content designed to pass automated screening software and appeal to human recruiters.

Your primary goal is to process the User Information provided, tailor it *specifically* to the target Job Description according to ATS best practices, and then structure the final resume content into a **JSON object format**. This JSON output will be used to programmatically populate a resume template.

**Mandatory Inputs You Require:**

1.  **Complete User Information:** This must include:
    * Full Name & Contact Details (Phone, Email, Location [City, State/Country], LinkedIn URL)
    * Work Experience (Company Name, Job Title, Dates of Employment [Month, Year], Location, Detailed Responsibilities and Quantifiable Achievements - ideally using STAR method bullets: Situation, Task, Action, Result)
    * Education (Institution Name, Degree(s) Earned, Graduation Dates [Month, Year], Location, Relevant Coursework/Honors if applicable)
    * Skills Section (Categorized list of technical skills, software proficiency, languages, soft skills, certifications)
    * Optional: Professional Summary or Objective statement preference.

2.  **The Complete Target Job Description:** This is essential for keyword analysis and tailoring.

**Instructions for Content Generation and Structuring:**

1.  **Analyze and Integrate Keywords:** Meticulously scan the provided Job Description. Identify essential keywords, skills (hard and soft), qualifications, industry jargon, and specific requirements. Integrate these *exact* keywords and phrases naturally and appropriately into the content that will populate the JSON fields (especially `summary`, `skills`, and `workExperience.responsibilities`). Ensure both full terms and acronyms are used where relevant (e.g., "Customer Relationship Management (CRM)"). Avoid unnatural keyword stuffing.
2.  **Apply ATS Best Practices to Content:**
    * Ensure bullet points under `workExperience.responsibilities` start with strong action verbs and quantify achievements whenever possible based on user input.
    * Use standard, consistent date formats (e.g., "Month, YYYY" or "MM/YYYY") for all date fields in the JSON.
    * Maintain a professional and concise tone in all text fields.
    * Ensure perfect spelling and grammar in all string values within the JSON.
3.  **Standard Sections Logic:** Mentally structure the resume using standard sections (Contact Info, Summary, Skills, Experience, Education, etc.) even though the output is JSON. Use standard section heading concepts to guide content placement within the JSON structure.
4.  **Output Format: JSON Object:**
    * Your final output MUST be a single, valid JSON object.
    * Structure the JSON object according to the following schema (adapt categories and include optional sections only if relevant data is provided):
"""


RESUME_PROMPT_TEMPLATE = """
{system_prompt}

User Information:
{user_info}

Target Job Description:
{job_description}

Generate an ATS-optimized resume in JSON format following these guidelines:
1. Analyze the job description for keywords and requirements
2. Tailor the user's information to match the job requirements but do not change the user information. Everything should be the same. If the user does not match the job requirements ask the user to select a different job role
3. Ensure all achievements are quantifiable
4. Use consistent date formatting
5. Include only relevant information
6. Structure the output as a valid JSON object

The output should follow this schema:
{{
  "personalInfo": {{
    "name": "",
    "phone": "",
    "email": "",
    "linkedin": "",
    "portfolio": "",
    "location": ""
  }},
  "summary": "",
  "experience": [...],
  "education": [...],
  "skills": {{
    "technical": [...],
    "professional": [...],
    "languages": [...]
  }},
  "projects": [...],
  "Estimated_ATS_Score": [...],
  "Recommendations:[]
  
}}

Return only the JSON object without any extra text and do not add ```. Also return the Estimated ATS score and its reason, The info is provided under the user information and job description section
.
"""

prompt_template = PromptTemplate(
    input_variables=["system_prompt", "user_info", "job_description"],
    template=RESUME_PROMPT_TEMPLATE,
)

@app.get("/")
def welcome():
    return {"message": "Welcome to the Resume Generator API!"}

@app.post("/generate-resume")
async def generate_resume(request: ResumeRequest):
    try:
        # Format user info as JSON string for prompt readability
        formatted_user_info = json.dumps(request.user_info, indent=2)

        # Format prompt
        prompt_str = prompt_template.format(
            system_prompt=SYSTEM_PROMPT,
            user_info=formatted_user_info,
            job_description=request.job_description
        )
        print(prompt_str)

        # Generate the resume
        response = llm.generate_content(prompt_str)
        # print(response.text.strip("`").lstrip("json").strip().strip("`"))

        try:
            parsed_data = json.loads(response.text.strip("`").lstrip("json").strip().strip("`"))
            # print(parsed_data)
            return parsed_data
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse JSON: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
