# Resume Builder Backend

This is the backend service for the Resume Builder application. It uses FastAPI, LangChain, and Google's Gemini AI to generate professional resumes based on user input.

## Setup

1. Activate the virtual environment:
   ```bash
   # On Windows
   .\venv\Scripts\activate

   # On Unix/MacOS
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Google API key:
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Copy the `.env` file and replace `your_google_api_key_here` with your actual API key

## Running the Server

1. Start the server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. The server will start at `http://localhost:8000`

## API Endpoints

### POST /generate-resume

Generates a professional resume based on the provided information.

Request body:
```json
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "location": "string",
  "linkedin": "string (optional)",
  "portfolio": "string (optional)",
  "summary": "string (optional)",
  "experience": [
    {
      "title": "string",
      "company": "string",
      "location": "string",
      "startDate": "string",
      "endDate": "string",
      "responsibilities": ["string"]
    }
  ],
  "education": [
    {
      "degree": "string",
      "institution": "string",
      "location": "string",
      "graduationYear": "string",
      "details": ["string"]
    }
  ],
  "skills": {
    "technical": ["string"],
    "professional": ["string"],
    "languages": ["string"]
  },
  "projects": [
    {
      "name": "string",
      "description": "string"
    }
  ]
}
```

The API will return a complete resume in the specified JSON format, with generated content for any missing fields and enhanced versions of provided information.

## Error Handling

The API includes proper error handling for:
- Missing or invalid API key
- Invalid input data
- Generation failures
- JSON parsing errors

## CORS

CORS is enabled for all origins in development. For production, update the CORS settings in `main.py` to only allow requests from your frontend domain. 