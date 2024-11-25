import requests

def upload_csv(file_path, url='http://localhost:8000/upload_crawled_data'):
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

if __name__ == "__main__":
    upload_csv('analysis_results.csv')