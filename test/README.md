# Test Files

This directory contains test scripts used during development to verify the SiliconFlow API OCR functionality.

## ocr_test.py

A simple test script that demonstrates how to call the SiliconFlow PaddleOCR API.

### Setup

Replace the empty `api_key` variable in the main() function with your SiliconFlow API key:

```python
api_key = "your_api_key_here"
```

### Usage

```bash
python3 ocr_test.py /path/to/image.jpg
```

### How It Works

This script demonstrates the basic API call flow:

1. Read the image file and convert to base64
2. Determine the MIME type based on file extension
3. Create an OpenAI client pointing to SiliconFlow's API endpoint
4. Send a chat completion request with the base64-encoded image
5. Print the recognized text

### Why This Approach

This minimal script was used for initial API testing to verify:
- API authentication works correctly
- Base64 image encoding is handled properly
- The OCR model returns expected results
- Error handling is adequate

After confirming the API works, the functionality was expanded into the full-featured `skills/ocr/scripts/ocr_skill.py`.

### Dependencies

```bash
pip install openai
```
