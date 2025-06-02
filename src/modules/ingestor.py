import os
import re
from modules.utils import extract_text_from_pdf
import requests
import uuid

class CV_Ingestor:
    """
    Class for handling the ingestion of CV data.
    """

    def ingest(self):
        """
        Ingests the CV data and processes it.

        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    def ingest_folder(self):
        """
        Ingests multiple CV files and processes them.

        """
        raise NotImplementedError("This method should be overridden by subclasses.")

class CV_Local_Ingestor(CV_Ingestor):
    """
    Class for handling the ingestion of local CV files.
    """

    def __init__(self):
        """
        Initializes the CV_Local_Ingestor with the path to a local CV file.

        """

    def ingest(self, file_path):
        """
        Ingests the local CV file and processes it.

        Parameters:
            file_path (str): The path to the local CV file.
        Returns:
            dict: A dictionary containing the file path and the raw text extracted from the PDF.
        """
        raw_text = extract_text_from_pdf(file_path)
        return {
            'file_path': file_path,
            'raw_text': raw_text
        }
    
    def ingest_folder(self, folder_path):
        """
        Ingests multiple local CV files from a specified folder and processes them.

        Parameters:
            folder_path (str): The path to the folder containing CV files.
        Returns:
            list: A list of dictionaries containing file paths and raw text extracted from each PDF.
        """
        raw_texts = []
        for filename in os.listdir(folder_path):
            if filename.endswith('.pdf'):
                file_path = os.path.join(folder_path, filename)
                try:
                    data = extract_text_from_pdf(file_path)
                    raw_texts.append(data)
                except Exception as e:
                    print(f"Error processing file {filename}: {str(e)}")
        return raw_texts
    
class CV_GDrive_Ingestor(CV_Ingestor):
    """
    Class for handling the ingestion of CV files from Google Drive.
    """

    def __init__(self):
        """
        Initializes the CV_GDrive_Ingestor with a Google Drive service instance.

        """
    
    def download_file(self, url, tmp_dir='tmp'):
        """
        Downloads a file from Google Drive.

        Parameters:
            url (str): The URL of the Google Drive file to download.
            tmp_dir (str): The directory to save the downloaded file.
        Returns:
            str: The path to the downloaded file.
        """
        # Check if the tmp_dir exists, if not create it
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
        if not match:
            raise ValueError("Invalid Google Drive URL format.")

        file_id = match.group(1)
        print(f"Extracted file ID: {file_id}")
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        file_path = os.path.join(tmp_dir, f"{uuid.uuid4()}_{file_id}.pdf")
        
        # Download the file from Google Drive
        response = requests.get(download_url)
        
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return file_path, download_url
        else:
            raise Exception(f"Failed to download file with ID {file_id}. Status code: {response.status_code}")

    def ingest(self, url, tmp_dir='tmp'):
        """
        Ingests the CV file from Google Drive and processes it.

        Parameters:
            url (str): The URL of the Google Drive file to download.
            tmp_dir (str): The directory to save the downloaded file.
        Returns:
            dict: A dictionary containing the file path and the raw text extracted from the PDF.
        """
        
        # Check if the tmp_dir exists, if not create it
        # Download the file from Google Drive
        file_path, gdrive_url = self.download_file(url, tmp_dir)
        if not file_path:
            raise Exception("File download failed.")
        raw_text = extract_text_from_pdf(file_path)
        
        return {
            'file_path': file_path,
            'raw_text': raw_text,
            'gdrive_url': gdrive_url
        }
    
    def ingest_folder(self, gdrive_folder_url, tmp_dir='tmp'):
        """
        Ingests multiple CV files from Google Drive and processes them.
        
        Parameters:
            gdrive_folder_url (str): The URL of the Google Drive folder containing CV files.
            tmp_dir (str): The directory to save the downloaded files.
        Returns:
            list: A list of dictionaries containing file paths and raw text extracted from each PDF.
        """
        raw_texts = []
        # This method would require additional logic to list files in a Google Drive folder
        # and download each file. For simplicity, we assume the folder contains only PDF files.
        # In practice, you would use Google Drive API to list files in the folder.
        # Here we just simulate the process with a single file for demonstration.
        import gdown
        gdrive_folder_id = gdrive_folder_url.split('/')[-1].split('?')[0]
        gdown.download_folder(f'https://drive.google.com/drive/folders/{gdrive_folder_id}', output=tmp_dir, use_cookies=False)
        for filename in os.listdir(tmp_dir):
            if filename.endswith('.pdf'):
                file_path = os.path.join(tmp_dir, filename)
                try:
                    raw_text = extract_text_from_pdf(file_path)
                    raw_texts.append(raw_text)
                except Exception as e:
                    print(f"Error processing file {filename}: {str(e)}")
        # Clean up temporary directory if not pdf files 
        for filename in os.listdir(tmp_dir):
            if not filename.endswith('.pdf'):
                os.remove(os.path.join(tmp_dir, filename))

        return {
            'gdrive_folder_url': gdrive_folder_url,
            'raw_texts': raw_texts,
            'file_paths': [filename for filename in os.listdir(tmp_dir) if filename.endswith('.pdf')]
        }
if __name__ == "__main__":
    # Example usage
    # local_ingestor = CV_Local_Ingestor()
    # local_data = local_ingestor.ingest('data/CV_PhanNguyenMinhKhoi_AI.pdf')
    # print(local_data)

    gdrive_ingestor = CV_GDrive_Ingestor()
    # gdrive_data = gdrive_ingestor.ingest('https://drive.google.com/file/d/1m3yfJG7PRp4j8NaXA6dj0EDvCDKwlFcz/view?usp=sharing')
    # print(gdrive_data)
    texts = gdrive_ingestor.ingest_folder("https://drive.google.com/drive/folders/1D2fcO5g8laj9nAZN5x-ZxAflnQ5ZCWDW?usp=sharing")
    print(texts)