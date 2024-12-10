import os
import logging
from flask import Flask, request, send_from_directory
from werkzeug.utils import secure_filename

class FileServer:
    def __init__(self, upload_folder='received_files', max_content_length=16 * 1024 * 1024):
        """
        Initialize the file server with upload configurations
        
        Args:
            upload_folder (str): Directory to store uploaded files
            max_content_length (int): Maximum file size allowed
        """
        self.app = Flask(__name__)
        
        # Ensure upload directory exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # Configuration
        self.app.config['UPLOAD_FOLDER'] = upload_folder
        self.app.config['MAX_CONTENT_LENGTH'] = max_content_length
        
        # Setup logging
        logging.basicConfig(filename='server.log', level=logging.INFO)
        
        # Define routes
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes for file upload and download"""
        self.app.route('/upload', methods=['POST'])(self.upload_file)
        self.app.route('/download/<filename>', methods=['GET'])(self.download_file)
    
    def upload_file(self):
        """Handle file upload"""
        if 'file' not in request.files:
            return {'error': 'No file part'}, 400
        
        file = request.files['file']
        
        if file.filename == '':
            return {'error': 'No selected file'}, 400
        
        try:
            # Secure filename to prevent directory traversal
            filename = secure_filename(file.filename)
            file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
            
            # Save file
            file.save(file_path)
            
            # Log successful upload
            logging.info(f"File uploaded: {filename}")
            
            return {'message': 'File uploaded successfully', 'filename': filename}, 200
        
        except Exception as e:
            logging.error(f"Upload error: {str(e)}")
            return {'error': str(e)}, 500
    
    def download_file(self, filename):
        """Handle file download"""
        try:
            return send_from_directory(
                self.app.config['UPLOAD_FOLDER'], 
                filename, 
                as_attachment=True
            )
        except FileNotFoundError:
            logging.error(f"Download failed: {filename} not found")
            return {'error': 'File not found'}, 404
    
    def run(self, host='0.0.0.0', port=5000):
        """Start the Flask server"""
        self.app.run(host=host, port=port)

def main():
    server = FileServer()
    server.run()

if __name__ == '__main__':
    main()