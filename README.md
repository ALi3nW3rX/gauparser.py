# URL Status Checker

A Python script to parse, validate, and filter a list of URLs from a text file. The script checks if the URLs return a valid HTTP status code and filters out unwanted URLs based on file extensions and patterns.

## Features

- **Multithreaded**: Efficiently checks multiple URLs concurrently using threading.
- **File Type Filtering**: Excludes URLs with unwanted file extensions (e.g., `.js`, `.css`, `.png`) while including document file types (e.g., `.pdf`, `.docx`, `.xlsx`).
- **Pattern Matching**: Filters out URLs based on defined patterns, such as `wp-json`, `embed`, and API endpoints.
- **File Type Extraction**: Extracts and displays the file type from the URL path.
- **Progress Bar**: Provides a visual progress indicator to show script execution status.
- **CSV Output**: Saves the valid URLs, HTTP status codes, and file types to a CSV file.

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/yourusername/url-status-checker.git
    cd url-status-checker
    ```

2. **Create a virtual environment** (optional but recommended):

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required packages**:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

```bash
python3 gauparser.py -f <input_file> -o <output_file> -c <status_codes> -t <threads>

