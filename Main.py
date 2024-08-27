import pyautogui
import datetime
import os
import threading
import time
from PIL import Image, ImageFilter
import traceback
import requests
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import io
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ActivityTracker:
    def __init__(self, config_url: str, bucket_name: str, s3_prefix: str = ''):
        self.config_url = config_url
        self.bucket_name = bucket_name
        self.s3_prefix = s3_prefix
        
        # Initialize S3 client with hardcoded credentials
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )

        # Load configuration with fallback values
        self.config = self.load_config()
        self.screenshot_interval = self.config.get('screenshot_interval', 300)  # Default 5 minutes
        self.screenshot_blurred = self.config.get('screenshot_blurred', False)
        
        self.stop_event = threading.Event()
        self.config_update_interval = 60  # Check every minute
        self.track_activity_thread = threading.Thread(target=self.track_activity)
        self.update_config_thread = threading.Thread(target=self.update_config)
        self.track_activity_thread.start()
        self.update_config_thread.start()

    def load_config(self) -> dict:
        try:
            response = requests.get(self.config_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.ConnectionError:
            print("No internet connection. Cannot load configuration. Using default values.")
            return {}
        except requests.exceptions.HTTPError as e:
            print(f"Failed to load configuration: {e}. Using default values.")
            return {}
        except Exception as e:
            print(f"Failed to load configuration: {e}. Using default values.")
            return {}

    def update_config(self):
        while not self.stop_event.is_set():
            try:
                new_config = self.load_config()
                if new_config != self.config and new_config:  # Only update if the new config is valid
                    self.config = new_config
                    self.screenshot_interval = self.config.get('screenshot_interval', 600)
                    self.screenshot_blurred = self.config.get('screenshot_blurred', False)
                    print("Configuration updated.")
            except Exception as e:
                print(f"Failed to update configuration: {e}")
            time.sleep(self.config_update_interval)

    def capture_screenshot(self, blurred: bool = False) -> Image:
        screenshot = pyautogui.screenshot()
        if blurred:
            screenshot = screenshot.filter(ImageFilter.GaussianBlur(5))
        return screenshot

    def save_screenshot(self, screenshot: Image, filename: str):
        try:
            # Convert screenshot to bytes
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Upload to S3
            s3_key = os.path.join(self.s3_prefix, filename)
            self.s3_client.upload_fileobj(img_byte_arr, self.bucket_name, s3_key)
            print(f"Screenshot uploaded to S3 at {s3_key}")
        except NoCredentialsError:
            print("Credentials not available for S3.")
        except PartialCredentialsError:
            print("Incomplete credentials provided for S3.")
        except Exception as e:
            print(f"Failed to upload screenshot to S3: {e}")

    def track_activity(self):
        while not self.stop_event.is_set():
            timestamp = datetime.datetime.now()
            filename = f"screenshot_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
            screenshot = self.capture_screenshot(self.screenshot_blurred)
            self.save_screenshot(screenshot, filename)
            time.sleep(self.screenshot_interval)

    def stop(self):
        self.stop_event.set()
        self.track_activity_thread.join()
        self.update_config_thread.join()
        print("Activity tracker stopped.")

    def handle_exception(self, e: Exception):
        print(f"An error occurred: {e}")
        traceback.print_exc()

    def run(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            self.handle_exception(e)
            self.stop()

if __name__ == "__main__":
    config_url = 'http://localhost:8001/config.json'  # add your own config_url
    bucket_name = 'my-first-buckettt'  # add your own bucket name
    s3_prefix = 'screenshots'  # Optional prefix for organizing files in S3

    tracker = ActivityTracker(config_url, bucket_name, s3_prefix)
    tracker.run()
