import os
import re
import pdfplumber
import requests

class CV_Ingestor:
    """
    Class for handling the ingestion of CV data.
    """

    def ingest(self):
        """
        Ingests the CV data and processes it.

        :return: Processed CV data.
        """
        pass

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

        :return: Processed CV data.
        """
        raw_text = ""
        if file_path.endswith('.pdf'):
            try:
                with pdfplumber.open(file_path) as pdf:
                    text = "\n".join([page.extract_text() or "" for page in pdf.pages])
                    raw_text = raw_text + text
            except Exception as e:
                raise Exception(f"Error reading PDF file: {str(e)}")
        return {
            'file_path': file_path,
            'raw_text': text
        }
    
class CV_GDrive_Ingestor(CV_Ingestor):
    """
    Class for handling the ingestion of CV files from Google Drive.
    """

    def __init__(self):
        """
        Initializes the CV_GDrive_Ingestor with a Google Drive service instance.

        :param drive_service: The Google Drive service instance.
        """
    
    def download_file(self, url, tmp_dir='./tmp'):
        """
        Downloads a file from Google Drive.

        :param file_id: The ID of the file to download.
        :param tmp_dir: The directory to save the downloaded file.
        :return: The path to the downloaded file.
        """
        # Check if the tmp_dir exists, if not create it
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
        if not match:
            raise ValueError("Invalid Google Drive URL format.")

        file_id = match.group(1)
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        file_path = os.path.join(tmp_dir, f"{file_id}.pdf")
        
        # Download the file from Google Drive
        response = requests.get(download_url)
        
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return file_path
        else:
            raise Exception(f"Failed to download file with ID {file_id}. Status code: {response.status_code}")

    def ingest(self, url, tmp_dir='tmp'):
        """
        Ingests the CV file from Google Drive and processes it.

        :return: Processed CV data.
        """
        
        # Check if the tmp_dir exists, if not create it
        # Download the file from Google Drive
        file_path = self.download_file(url, tmp_dir)
        if not file_path:
            raise Exception("File download failed.")
        raw_text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join([page.extract_text() or "" for page in pdf.pages])
                raw_text = raw_text + text
        except Exception as e:
            raise Exception(f"Error reading PDF file: {str(e)}")
        return {
            'file_path': file_path,
            'raw_text': raw_text
        }

if __name__ == "__main__":
    # Example usage
    local_ingestor = CV_Local_Ingestor()
    local_data = local_ingestor.ingest('data/CV_PhanNguyenMinhKhoi_AI.pdf')
    print(local_data)

    gdrive_ingestor = CV_GDrive_Ingestor()
    gdrive_data = gdrive_ingestor.ingest('https://drive.google.com/file/d/1m3yfJG7PRp4j8NaXA6dj0EDvCDKwlFcz/view?usp=sharing')
    print(gdrive_data)