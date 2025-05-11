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
git clone https://github.com/Shoukhin1803078/Niyog_task_1_solution.git
cd Niyog_task_1_solution
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
### Step-4 : Configure OpenAI API Key
```
Locate OPENAI_API_KEY in task1/settings.py and replace it with your API key:
OPENAI_API_KEY = 'openai-api-key-here'
```

### Step-5 : Start the Development Server
```
cd task1
python manage.py runserver
```

The API will be available at http://127.0.0.1:8000/api/scrape-and-answer/


### Request Format
{
  "url": "https://example.com",
  "question": "What is the main topic of this website?"
}
### Response Format
{
  "answer": "The main topic of this website is [topic]."
}


# My output (API Endpoint Test):
<img width="1710" alt="Screenshot 2025-05-11 at 1 04 26 PM" src="https://github.com/user-attachments/assets/f61f55bd-c26b-405a-892c-c5d10457a2c7" />

