# Niyog_task_2_solution

# Web Scraping with LLM Integration

I created this FastAPI application that allows users to upload a PDF document and ask questions about its content. The application extracts text from the PDF and uses OpenAI's GPT models to generate accurate answers based on the document content.

#### Prerequisites
- Python 3.8+
- FastAPI
- PyPDF2
- OpenAI API key


## Installation

### Step-1 : Clone the Repository

```
https://github.com/Shoukhin1803078/Niyog_task_2_solution.git
cd Niyog_task_2_solution
```

### Step-2 : Create a virtual environment and activate it
```
python -m venv venv
# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step-3 : Install Dependencies 
```
pip install -r requirements.txt
```
### Step-4 : Create .env file and Configure OpenAI API Key into .env
```
OPENAI_API_KEY = 'openai-api-key-here'
```

### Step-5 : Start the Development Server
```
uvircorn main:app --reload
or 
python main.py
```

The API will be available at http://localhost:8000
In swagger UI API will be at http://localhost:8000/docs



### Response Format
{
  "message": "PDF successfully uploaded and processing started"
}
### Request Format
{
  "question": "What is the main topic of the document?"
}
### Response Format
{
  "answer": "The main topic of the document is artificial intelligence applications in healthcare."
}


# My output (API Endpoint Test):
<img width="1710" alt="Screenshot 2025-05-11 at 5 05 23 PM" src="https://github.com/user-attachments/assets/5600516d-ec94-428f-aa82-f9f6d6104840" />
<img width="1710" alt="Screenshot 2025-05-11 at 4 45 21 PM" src="https://github.com/user-attachments/assets/117e3e0a-58f8-4bd6-aeae-63819528977b" />
<img width="1710" alt="Screenshot 2025-05-11 at 4 46 01 PM" src="https://github.com/user-attachments/assets/11aedff1-3165-43fa-9b99-3b073e57c415" />
<img width="1710" alt="Screenshot 2025-05-11 at 4 46 10 PM" src="https://github.com/user-attachments/assets/28824953-216c-4f28-96de-a1bbb64f0387" />


