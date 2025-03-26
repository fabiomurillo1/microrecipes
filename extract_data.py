import zipfile
import os

zip_path = "C:/Users/fabio/Desktop/pythonProject4/food-com-recipes-and-user-interactions.zip"
extract_path = "C:/Users/fabio/Desktop/pythonProject4/data"

# Create 'data' directory if it doesn't exist
os.makedirs(extract_path, exist_ok=True)

# Extract ZIP file
with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(extract_path)

print(f"Dataset extracted to: {extract_path}")