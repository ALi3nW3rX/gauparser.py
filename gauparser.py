import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import csv
import logging
import os
from tqdm import tqdm  # Progress bar library
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(filename='errors.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define a list of file extensions to filter out
exclude_extensions = [
    '.svg', '.jpg', '.jpeg', '.webp', '.png', '.gif', '.bmp', '.tiff', '.ico',  # Image extensions
    '.js', '.css', '.eot', '.woff', '.woff2', '.ttf', '.mp4', '.avi', '.mp3'  # Asset extensions
    # Document extensions are not included in the exclusion list
]

# Define a list of patterns to identify unwanted URLs
unwanted_patterns = [
    'wp-json', 'embed', 'oembed', '?', 'api', 'json', 'wp-content', 'plugins', 'vendor', 'cdn', 'static'
]

# Function to check if a URL returns a valid status code and get the file type
def check_url(url, valid_codes):
    try:
        response = requests.head(url, timeout=5)
        if response.status_code in valid_codes:
            file_type = get_file_type(url)
            return (url, response.status_code, file_type)
    except requests.RequestException as e:
        logging.error(f"Error checking {url}: {e}")
    return None

# Function to filter out URLs with specific unwanted extensions
def is_unwanted_extension(url):
    return any(url.lower().endswith(ext) for ext in exclude_extensions)

# Function to filter out unwanted URLs based on patterns
def is_unwanted_url(url):
    # Check if the URL is from "wp-content/uploads" and allow it unless it has an unwanted extension
    if "wp-content/uploads" in url.lower() and not is_unwanted_extension(url):
        return False
    # If the URL contains any unwanted patterns and is not an exception, exclude it
    return any(pattern in url.lower() for pattern in unwanted_patterns)

# Function to get the file type from the URL
def get_file_type(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    if '.' in path:
        return path.split('.')[-1]
    return 'unknown'

# Main function
def main(file, output_file, valid_codes, max_threads):
    # Read the file and get the URLs
    with open(file, 'r') as f:
        urls = [line.strip().split(",")[0] for line in f if line.strip()]  # Split to remove trailing ',200'

    # Filter out URLs with unwanted extensions and patterns
    urls = [url for url in urls if not is_unwanted_extension(url) and not is_unwanted_url(url)]

    valid_urls = []

    # Progress bar setup with dynamic column width and leave=True
    with tqdm(total=len(urls), desc="Processing URLs", ncols=100, dynamic_ncols=True, leave=True) as pbar:
        # Use ThreadPoolExecutor to check URLs concurrently
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_url = {executor.submit(check_url, url, valid_codes): url for url in urls}
            
            for future in as_completed(future_to_url):
                try:
                    result = future.result()
                    if result:
                        valid_urls.append(result)
                except Exception as e:
                    logging.error(f"Error processing result: {e}")
                pbar.update(1)  # Update progress bar for each completed URL

    # Save valid URLs to the output file
    if valid_urls:
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['URL', 'Status Code', 'File Type']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for url, status_code, file_type in valid_urls:
                writer.writerow({'URL': url, 'Status Code': status_code, 'File Type': file_type})
        print(f"\nValid URLs have been saved to {output_file}")
    else:
        print("\nNo valid URLs found.")

# Argument parser
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check URLs for valid status codes.")
    parser.add_argument("-f", "--file", required=True, help="Input file with URLs.")
    parser.add_argument("-o", "--output", default="valid_urls.csv", help="Output file for valid URLs.")
    parser.add_argument("-c", "--codes", default="200", help="Comma-separated list of valid status codes (e.g., 200,301,302).")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads to use for concurrent checking.")
    args = parser.parse_args()

    # Convert the status codes into a list of integers
    valid_status_codes = list(map(int, args.codes.split(',')))

    # Run the main function with provided arguments
    main(args.file, args.output, valid_status_codes, args.threads)
