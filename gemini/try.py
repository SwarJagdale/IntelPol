import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from pathlib import Path
import pandas as pd
import PyPDF2
import openai
import json
openai.api_key="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"

def configure_genai(api_key):
    """Configure the Gemini AI API."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')


def download_pdfs(url, headers, limit=3):
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


def main():
    """Main function to execute the PDF analysis pipeline."""
    GEMINI_API_KEY = "AIzaSyCgtKi9n_7xnPBAlXnJjPVbrv1gWQQ-4ZY"
    URL = "https://nandedpolice.gov.in/publish/13"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }

    model = configure_genai(GEMINI_API_KEY)

    # Download PDFs
    pdf_files = download_pdfs(URL, HEADERS)
    if not pdf_files:
        print("No PDFs found to analyze.")
        return

    # Analyze PDFs
    all_results = pd.DataFrame()
    for pdf_file in pdf_files:
        pdf_content = extract_text_from_pdf(pdf_file)
        if pdf_content:
            results = analyze_pdf(model, pdf_content)
            print("got results")
            print(results)
            all_results = pd.concat([all_results, results], ignore_index=True)

    # Save results
    if not all_results.empty:
        save_results(all_results)
    else:
        print("No results to save.")

    for pdf_file in pdf_files:
        #delete
        import os
        os.remove(pdf_file)

if __name__ == "__main__":
    main()
