# streamlit-app

A Streamlit application to scrape Instagram profile data and provide a download link for the results.

## Features

*   Input an Instagram profile name or URL.
*   Select the desired output file format (CSV or JSON).
*   Calls an external API to process the request.
*   Polls an S3 bucket for the generated file.
*   Provides a pre-signed S3 URL to download the file (valid for 24 hours).

## Prerequisites

*   Python 3.x
*   pip

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd streamlit-app
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment Variables:**
    Create a file named `.env` inside the `app` directory ([app/.env](app/.env)) with the following content:
    ```dotenv
    BUCKET_S3="your-s3-bucket-name"
    API_ENDPOINT="your-api-gateway-endpoint-url"
    ```
    Replace `"your-s3-bucket-name"` and `"your-api-gateway-endpoint-url"` with your actual S3 bucket name and API endpoint URL.

## Running the App

Navigate to the project's root directory in your terminal and run:

```bash
streamlit run app/page.py
```

This will start the Streamlit application, and you can access it in your web browser at the provided local URL.

## Environment Variables

*   `BUCKET_S3`: The name of the AWS S3 bucket where the generated files are stored.
*   `API_ENDPOINT`: The URL of the API Gateway endpoint that triggers the Instagram scraping process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
