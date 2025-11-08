# Telecom SMB Churn Health Dashboard

This Streamlit application predicts customer churn risk and provides a tool to send personalized emails to high-risk customers using a generative AI model.

## Installation

1.  Clone the repository.
2.  Install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

### 1. Generative AI API Key

This application uses Google's Generative AI to generate personalized emails. You need to provide a Gemini API key.

-   Set the `GEMINI_API_KEY` environment variable to your API key.

    ```bash
    export GEMINI_API_KEY="YOUR_API_KEY"
    ```

### 2. SMTP Configuration for Sending Emails

To send emails, you need to configure your SMTP server settings as environment variables.

-   `SMTP_FROM_EMAIL`: The email address you are sending from.
-   `SMTP_SERVER`: The address of your SMTP server (e.g., `smtp.gmail.com`).
-   `SMTP_PORT`: The port of your SMTP server (e.g., `587` for TLS).
-   `SMTP_USER`: The username for your SMTP server (often your email address).
-   `SMTP_PASSWORD`: The password for your SMTP server.

    ```bash
    export SMTP_FROM_EMAIL="your_email@example.com"
    export SMTP_SERVER="smtp.example.com"
    export SMTP_PORT="587"
    export SMTP_USER="your_username"
    export SMTP_PASSWORD="your_password"
    ```

    **Note:** For services like Gmail, you may need to use an "App Password" instead of your regular password.

## How to Run

1.  Make sure you have set the environment variables as described above.
2.  Run the Streamlit application:
    ```bash
    streamlit run streamlit_app.py
    ```
3.  Open your web browser and go to the URL provided by Streamlit.
4.  Upload a CSV file with customer data to see the churn predictions and send emails.
