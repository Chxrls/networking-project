import os
import requests
import logging
from typing import Dict, Union

class FileTransferClient:
    def __init__(self, base_url='http://localhost:5000'):
        """
        Initialize the file transfer client
        
        Args:
            base_url (str): Base URL of the file transfer server
        """
        self.base_url = base_url
        
        # Setup logging
        logging.basicConfig(filename='client.log', level=logging.INFO)
    
    def upload_file(self, filepath: str) -> Dict[str, Union[str, int]]:
        """
        Upload a file to the server
        
        Args:
            filepath (str): Path to the file to upload
        
        Returns:
            Dict containing upload result
        """
        if not os.path.exists(filepath):
            logging.error(f"File not found: {filepath}")
            return {'error': 'File not found', 'status': 404}
        
        try:
            with open(filepath, 'rb') as file:
                files = {'file': (os.path.basename(filepath), file)}
                response = requests.post(f"{self.base_url}/upload", files=files)
            
            # Log upload attempt
            if response.status_code == 200:
                logging.info(f"Successfully uploaded {filepath}")
            else:
                logging.error(f"Upload failed: {response.text}")
            
            return {
                'status': response.status_code,
                'message': response.json().get('message', 'Unknown response')
            }
        
        except requests.RequestException as e:
            logging.error(f"Network error during upload: {str(e)}")
            return {'error': str(e), 'status': 500}
    
    def download_file(self, filename: str, save_path: str = None) -> Dict[str, Union[str, int]]:
        """
        Download a file from the server
        
        Args:
            filename (str): Name of file to download
            save_path (str, optional): Path to save downloaded file
        
        Returns:
            Dict containing download result
        """
        try:
            response = requests.get(f"{self.base_url}/download/{filename}", stream=True)
            
            if response.status_code != 200:
                logging.error(f"Download failed: {response.text}")
                return {'error': 'Download failed', 'status': response.status_code}
            
            # Determine save path
            if save_path is None:
                save_path = os.path.join(os.getcwd(), filename)
            
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            logging.info(f"Successfully downloaded {filename}")
            return {
                'status': 200,
                'message': 'File downloaded successfully',
                'path': save_path
            }
        
        except requests.RequestException as e:
            logging.error(f"Network error during download: {str(e)}")
            return {'error': str(e), 'status': 500}

def main():
    client = FileTransferClient()
    # Example usage
    upload_result = client.upload_file('example.txt')
    print(upload_result)

if __name__ == '__main__':
    main()