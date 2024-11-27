from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
import openai
import google.generativeai as genai
from pathlib import Path
import pandas as pd
import PyPDF2
import requests
from bs4 import BeautifulSoup
import json
import dotenv
dotenv.load_dotenv()

sys.path.append(str(Path(__file__).resolve().parent.parent / 'gemini'))
openai.api_key=os.getenv('OPENAI_API_KEY')

def configure_genai(api_key):
    """Configure the Gemini AI API."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')


def download_pdfs(url, headers, limit=5):
    """Download PDF files from the given URL."""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        pdf_links = [
            link['href'] for link in soup.find_all("a", href=True)
            if ".pdf" in link['href'].lower() and link['href'].startswith("http")
        ][:limit]

        pdf_files = [save_pdf(link, headers) for link in pdf_links]
        return [file for file in pdf_files if file]
    except requests.RequestException as e:
        print(f"Error downloading PDFs: {e}")
        return []


def save_pdf(pdf_url, headers):
    """Save a PDF file from the given URL."""
    try:
        response = requests.get(pdf_url, headers=headers)
        response.raise_for_status()

        file_name = Path(pdf_url).name
        base_name = Path(file_name).stem
        extension = Path(file_name).suffix

        # Handle filename conflicts
        counter = 1
        while Path(file_name).exists():
            file_name = f"{base_name}_{counter}{extension}"
            counter += 1

        with open(file_name, "wb") as file:
            file.write(response.content)
        print(f"Downloaded: {file_name}")
        return file_name
    except requests.RequestException as e:
        print(f"Error saving PDF {pdf_url}: {e}")
        return None


def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file."""
    try:
        pdf_content = ""
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                pdf_content += page.extract_text()
        return pdf_content
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        return ""


def analyze_pdf(model, pdf_content):
    """Analyze PDF content using the Gemini API."""
    try:
        prompt = f"""
        Please analyze this PDF document and extract the following information in a structured format:
        - Case Number
        - Section of Law
        - Date
        - Location
        - Complainant
        - Accused
        - Important Details

        Please translate all content to English if it's in another language.
        Return a json response with the structured information usch that it can be parsed by pandas.read_json
        PDF Content:
        {pdf_content}
        """
        def generate_openai(prompt,max_tokens=2000,temperature=0.3,model='gpt-4o-mini',json_parse=False):
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            if json_parse:
                result = response.choices[0].message.content.replace("```json","").replace("```","")
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    print("Error parsing JSON")
                    print(result)
                    
            else :
                result = response.choices[0].message.content
            return result
        response = generate_openai(prompt)
        response = response.split("```json")[1].split("```")[0]
        response_text = response
        
        # response_text = response.text.replace("|", ",")
        with open('response.json', 'w') as f:
            f.write(response_text)
        return structure_response(response_text)
    except Exception as e:
        print(f"Error analyzing PDF content: {e}")
        return pd.DataFrame()


def structure_response(response_text):
    """Structure the response from Gemini API into a DataFrame."""
    try:
        print(response_text)
        df = pd.DataFrame(columns=[
            'Case Number', 'Section of Law', 'Date', 'Location',
            'Complainant', 'Accused', 'Details'
        ])
        # Parse response_text into DataFrame (adjust based on response format)
        
        df = pd.read_json('response.json')
        
        print(df.head(2))
        
        
        
        
        return df
    except Exception as e:
        print(f"Error structuring response: {e}")
        return pd.DataFrame()


def save_results(df, output_file='analysis_results.csv'):
    """Save analysis results to a CSV file."""
    try:
        df.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")


def upload_csv(file_path, url='http://backend:8000/upload_crawled_data'):
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'text/csv')}
        try:
            response = requests.post(url, files=files)
            if response.status_code == 200:
                print("File uploaded successfully.")
            else:
                print(f"Failed to upload file. Status code: {response.status_code}")
                print("Response:", response.json())
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)



# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 11, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'gemini_analysis_dag',
    default_args=default_args,
    description='A DAG to analyze PDFs using Gemini API',
    schedule_interval=timedelta(minutes=5),
    catchup=False,
)

# Define the tasks
def download_pdfs_task(**kwargs):
    url = "https://nandedpolice.gov.in/publish/13"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    pdf_files = download_pdfs(url, headers)
    return pdf_files
    

def analyze_pdfs_task(pdf_files,**kwargs):
    
    all_results = pd.DataFrame()
    for pdf_file in pdf_files:
        pdf_content = extract_text_from_pdf(pdf_file)
        if pdf_content:
            results = analyze_pdf(None, pdf_content)  # Pass the model if needed
            all_results = pd.concat([all_results, results], ignore_index=True)
    return all_results

def save_results_task(all_results,**kwargs):
    
    if not all_results.empty:
        save_results(all_results)
    else:
        print("No results to save.")
    
        
        
def start():
    pdf_files = download_pdfs_task()
    all_results = analyze_pdfs_task(pdf_files)
    save_results_task(all_results)
    upload_csv('analysis_results.csv')
    for file in pdf_files:
        os.remove(file)
    os.remove('response.json')
    
    



start_dag = PythonOperator(
    task_id='start',
    python_callable=start,
    provide_context=True,
    dag=dag,
)

start_dag