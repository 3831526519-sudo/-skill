import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Set a dummy API key so that the DeepSeek API call will fail and we test the fallback
os.environ['DEEPSEEK_API_KEY'] = 'dummy_key_for_testing'

# Add the current directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_generate_endpoint():
    """Test the /generate endpoint with a simple POST request."""
    with app.test_client() as client:
        # Prepare form data
        data = {
            'topic': '人工智能伦理',
            'word_count': '500',
            'structure': 'three-part',
            'has_illustration': 'on'  # This will be present if checkbox is checked
        }
        # Note: for file upload, we would need to include a file, but we can skip for now
        # or we can include a dummy file
        
        # We'll also include a dummy file for the illustration
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
            tmp_img.write(b'fake image data')
            tmp_img_path = tmp_img.name
        
        try:
            # Prepare the data for file upload
            data = {
                'topic': '人工智能伦理',
                'word_count': '500',
                'structure': 'three-part',
                'has_illustration': 'on'
            }
            files = {
                'illustration': ('test.png', open(tmp_img_path, 'rb'), 'image/png')
            }
            
            # Make the request
            response = client.post('/generate', data=data, files=files, content_type='multipart/form-data')
            
            # Check the response
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            assert 'application/octet-stream' in response.content_type or \
                   'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in response.content_type, \
                   f"Expected content type for .docx, got {response.content_type}"
            
            # Check that the response contains data
            assert len(response.data) > 0, "Response data is empty"
            
            # Check the headers for filename
            content_disposition = response.headers.get('Content-Disposition')
            assert content_disposition is not None, "Content-Disposition header is missing"
            assert '.docx' in content_disposition, f"Expected .docx in Content-Disposition: {content_disposition}"
            
            print("SUCCESS: /generate endpoint returned a valid .docx file")
            
        finally:
            # Clean up the temporary file
            if os.path.exists(tmp_img_path):
                os.unlink(tmp_img_path)

if __name__ == '__main__':
    try:
        test_generate_endpoint()
        print("All tests passed!")
    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)