# Telecom SMB Churn Health Dashboard

This Streamlit application predicts customer churn risk and provides a tool to send personalized emails to high-risk customers using a generative AI model.

## Features

-   **Churn Prediction:** Upload a CSV file with customer data to predict churn risk and view a customer health dashboard.
-   **AI-Powered Email Generation:** Automatically generate personalized, empathetic emails for high-risk customers using Google's Generative AI.
-   **Email Outreach:** Send the generated emails directly from the application to the customers.
-   **Data Export:** Download the full list of customers with their predicted health scores.

## Project Structure

```
/
├───.gitignore
├───README.md
├───requirements.txt
├───streamlit_app.py
├───saves/
│   ├───label_encoder.pkl
│   └───model.pkl
└───user_data/
    ├───fake_customers.py
    └───test_customers.csv
```

-   `streamlit_app.py`: The main Streamlit application file.
-   `requirements.txt`: A list of Python packages required to run the application.
-   `saves/`: This directory contains the pre-trained machine learning model (`model.pkl`) and the label encoder (`label_encoder.pkl`).
-   `user_data/`: This directory contains a script to generate fake customer data and the generated data itself.
    -   `fake_customers.py`: A script to generate a `test_customers.csv` file with synthetic customer data for testing the application.
    -   `test_customers.csv`: A sample CSV file with fake customer data.

## Installation

1.  Clone the repository.
2.  Install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Create a `.env` file in the root of the project and add the following environment variables:

```
GEMINI_API_KEY="YOUR_API_KEY"
SMTP_FROM_EMAIL="your_email@example.com"
SMTP_SERVER="smtp.example.com"
SMTP_PORT="587"
SMTP_USER="your_username"
SMTP_PASSWORD="your_password"
```

-   Replace the values with your actual credentials.
-   You can use the `.env.example` file as a template.

**Note:** For services like Gmail, you may need to use an "App Password" instead of your regular password.

## How to Run

1.  Make sure you have created the `.env` file as described in the `Configuration` section.
2.  Run the Streamlit application:
    ```bash
    streamlit run streamlit_app.py
    ```
3.  Open your web browser and go to the URL provided by Streamlit.
4.  Upload a CSV file with customer data to see the churn predictions and send emails. You can use the `user_data/test_customers.csv` file for testing.

## Generating Test Data

If you want to generate a new set of fake customer data, you can run the `fake_customers.py` script:

```bash
python user_data/fake_customers.py
```

This will create a new `test_customers.csv` file in the `user_data` directory.

## Docker Instructions

To build and run this application as a Docker container, follow these steps:

1.  **Build the Docker image:**
    ```bash
    docker build -t churn-health-dashboard .
    ```

2.  **Create a `.env` file:**
    -   Copy the `.env.example` file to a new file named `.env`.
    -   Update the `.env` file with your actual credentials.

3.  **Run the Docker container:**
    ```bash
    docker run -p 8501:8501 --env-file .env churn-health-dashboard
    ```

4.  Open your web browser and go to `http://localhost:8501`.
