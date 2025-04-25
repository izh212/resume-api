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

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini model
llm = genai.GenerativeModel('gemini-1.5-flash', generation_config=types.GenerationConfig(
    max_output_tokens=1024,
    temperature=1,
))

# Request body model
class ResumeRequest(BaseModel):
    user_info: Dict
    job_description: str

# System prompt
SYSTEM_PROMPT = """You are an expert Resume Assistant specializing in crafting ATS-optimized resume content designed to pass automated screening software and appeal to human recruiters.

Your primary goal is to process the User Information provided, tailor it *specifically* to the target Job Description according to ATS best practices, and then structure the final resume content into a **JSON object format**. This JSON output will be used to programmatically populate a resume template.

**Mandatory Inputs You Require:**

1. **Complete User Information:**
   - Full Name & Contact Details
   - Work Experience
   - Education
   - Skills Section
   - Optional: Professional Summary

2. **The Complete Target Job Description**

**Instructions:**
1. Analyze and integrate keywords from the job description.
2. Use ATS best practices and strong action verbs.
3. Format dates consistently.
4. Return a valid JSON object with proper spelling and grammar.
"""

# Prompt template with escaped curly braces
RESUME_PROMPT_TEMPLATE = """
{system_prompt}

User Information:
{user_info}

Target Job Description:
{job_description}

Generate an ATS-optimized resume in JSON format following these guidelines:
1. Analyze the job description for keywords and requirements.
2. Tailor the user's information to match the job requirements but do not change the user information. If the user does not match, recommend selecting a different job role.
3. Ensure all achievements are quantifiable.
4. Use consistent date formatting.
5. Include only relevant information.
6. Structure the output as a valid JSON object.
7.Also estimate the ATS score in Percentage based on the job description and user information.

The output should follow this schema:
{{
  "name": "",
  "title": "",
  "contact": {{
    "email": "",
    "phone": "",
    "location": "",
    "linkedIn": "",
    "github": "",
    "website": ""
  }},
  "summary": "",
  "areasOfExpertise": [],
  "achievements": [],
  "experience": [
    {{
      "company": "",
      "role": "",
      "location": "",
      "startDate": "",
      "endDate": "",
      "description": []
    }}
  ],
  "education": {{
    "institution": "",
    "degree": "",
    "startDate": "",
    "endDate": ""
  }},
  "skills": [],
  "projects": [
    {{
      "title": "",
      "description": "",
      "link": ""
    }}
  ],
  "Estimated_ATS_Score": [],
  "Recommendations": []
}}

Return only the JSON object without any extra text or markdown formatting.
"""


# Prompt formatter
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
        formatted_user_info = json.dumps(request.user_info, indent=2)

        try:
            prompt_str = prompt_template.format(
                system_prompt=SYSTEM_PROMPT,
                user_info=formatted_user_info,
                job_description=request.job_description
            )
            print("🔍 Prompt being sent to Gemini:\n", prompt_str)
        except Exception as prompt_err:
            raise HTTPException(status_code=500, detail=f"Prompt formatting failed: {str(prompt_err)}")

        # Generate response
        response = llm.generate_content(prompt_str)
        cleaned_response = response.text.strip("`").lstrip("json").strip().strip("`")

        try:
            parsed_data = json.loads(cleaned_response)
            return parsed_data
        except json.JSONDecodeError as json_err:
            raise HTTPException(status_code=500, detail=f"Failed to parse JSON: {str(json_err)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
