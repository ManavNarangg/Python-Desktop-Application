
# ActivityTracker

ActivityTracker is a Python application designed to take periodic screenshots of your desktop and upload them to an AWS S3 bucket. The application can be configured to capture screenshots at specified intervals and apply blur effects if required. It ensures that only one instance of the application runs at a time.

## Features
- Periodic Screenshots: Captures screenshots at configurable intervals.
- Blur Effect: Optionally applies a blur effect to screenshots.
- AWS S3 Integration: Uploads screenshots to an AWS S3 bucket.
- Single Instance Check: Ensures only one instance of the    application runs.

## Requirements
- Python 3.x
- pyautogui
- Pillow
- boto3
- requests

## Installation
    1. Clone the repository: git clone https://github.com/ManavNarangg/Python-Desktop-Application.git
    
    2. Install the required packages: pip install pyautogui Pillow boto3 requests

## Configuration
Before running the application, you need to configure the following:

- config_url: The URL where the configuration file is hosted. The configuration file should be in JSON format and may include parameters such as screenshot_interval and screenshot_blurred.
- bucket_name: The name of your AWS S3 bucket where screenshots will be uploaded.
- s3_prefix: (Optional) A prefix for organizing files in S3.

## Usage
- Edit the `Main.py` file to include your configuration:

```python
if __name__ == "__main__":
    config_url = 'http://localhost:8001/config.json'
    bucket_name = 'my-first-buckettt'
    s3_prefix = 'screenshots'

    tracker = ActivityTracker(config_url, bucket_name, s3_prefix)
    tracker.run()
```

- Run the application
```python 
python server.py
python Main.py
```

- Stopping the application: 
    You can stop the application by pressing Ctrl+C in the  terminal where it's running. The application will clean up and release the lock file.

## Error Handling
- Lock File Error: If the application detects that another instance is already running (indicated by the lock file), it will exit with an error message.
- Configuration Load Errors: If there are issues loading the configuration, default values will be used, and an error message will be displayed.
