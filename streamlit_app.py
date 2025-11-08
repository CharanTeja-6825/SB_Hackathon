import streamlit as st
import pandas as pd
import joblib
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import generativeai as genai
from dotenv import load_dotenv
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

# Load environment variables
load_dotenv()

# ================================
#  Load model and encoder (Safe Fallback)
# ================================
@st.cache_resource
def load_assets():
    model = joblib.load("saves/model.pkl")

    encoder_path = "saves/label_encoder.pkl"
    if os.path.exists(encoder_path):
        try:
            label_encoder = joblib.load(encoder_path)
        except Exception as e:
            st.warning(f"Error loading label encoder: {e}. Creating a new one.")
            label_encoder = LabelEncoder()
    else:
        st.info("Label encoder not found. Creating a new one.")
        label_encoder = LabelEncoder()

    return model, label_encoder

model, label_encoder = load_assets()

# ================================
#  Predict churn & health score
# ================================
def predict_health_scores(df):
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)

    if "customerID" in df.columns:
        ids = df["customerID"]
    else:
        ids = pd.Series(range(len(df)))

    df_features = df.copy()
    df_features = df_features.drop(columns=[c for c in ["customerID", "Churn"] if c in df_features])

    churn_prob = model.predict_proba(df_features)[:, 1]
    df["health_score"] = 1 - churn_prob

    df_sorted = df.sort_values("health_score").reset_index(drop=True)
    df_sorted["Rank"] = df_sorted.index + 1
    df_sorted["Risk_Level"] = pd.cut(
        df_sorted["health_score"],
        bins=[-0.01, 0.3, 0.7, 1.0],
        labels=["High Risk", "Medium Risk", "Healthy"]
    )
    return df_sorted

# ================================
#  Generate Email with AI
# ================================
def generate_email(customer_data):
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-pro-latest')
    except Exception as e:
        st.error(f"Error configuring Generative AI: {e}")
        return None

    prompt = f"""
    You are a customer retention specialist at a telecom company.
    A customer is at high risk of churning. Their details are:
    - Customer ID: {customer_data['customerID']}
    - Email: {customer_data['email']}
    - Complaint: {customer_data['complaint']}
    - Health Score: {customer_data['health_score']:.3f} (closer to 0 is worse)

    Write a personalized and empathetic HTML email to this customer.
    The goal is to acknowledge their issue, show that you are taking it seriously,
    and offer to help resolve it. Keep the tone professional and caring.
    Do not offer any discounts or promotions.
    Sign off as "Telcom Service Team".

    The email should be visually appealing and well-formatted.
    Use HTML tags to structure the email with headings, paragraphs, and bold text for emphasis.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating email: {e}")
        return None

# ================================
#  Send Email
# ================================
def send_email(to_address, subject, body):
    from_address = os.environ.get("SMTP_FROM_EMAIL")
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not all([from_address, smtp_server, smtp_port, smtp_user, smtp_password]):
        st.error("SMTP environment variables not set. Please configure them to send emails.")
        return False

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = f"Regarding your experience with our service (Customer ID: {to_address})"
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

# ================================
#  Streamlit UI
# ================================
st.set_page_config(page_title="Telecom SMB Churn Health Dashboard", layout="centered")

st.title("Telecom SMB Customer Health Dashboard")
st.caption("Predict churn risk and trigger retention automation through n8n")

uploaded_file = st.file_uploader("Upload your customer CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"File uploaded: {uploaded_file.name}")

    with st.spinner("Analyzing customer data..."):
        results = predict_health_scores(df)

    top_5 = results.sort_values("health_score").head(5)
    st.subheader("Top 5 High-Risk Customers")
    st.dataframe(
        top_5[["customerID", "email", "complaint", "health_score", "Risk_Level"]]
        .style.background_gradient(cmap="Reds", subset=["health_score"])
        .format({"health_score": "{:.3f}"})
    )

    st.markdown("---")
    st.markdown("### AI Agent: Autonomous Email Outreach")

    if "GEMINI_API_KEY" not in os.environ:
        st.warning("GEMINI_API_KEY environment variable not set. Email generation is disabled.")
    else:
        current_file_id = f"{uploaded_file.name}_{len(top_5)}"

        if f"emails_sent_{current_file_id}" not in st.session_state:
            st.info("AI Agent is automatically generating and sending emails to top 5 at-risk customers...")

            success_count = 0
            failed_count = 0
            email_reports = []

            with st.spinner("AI Agent: Generating personalized emails and sending..."):
                for _, row in top_5.iterrows():
                    customer_id = row["customerID"]
                    customer_email = row["email"]

                    email_content = generate_email(row)
                    if email_content:
                        subject = "Regarding your experience with our service"
                        if send_email(customer_email, subject, email_content):
                            success_count += 1
                            email_reports.append({
                                "customerID": customer_id,
                                "email": customer_email,
                                "status": "Sent",
                                "health_score": row["health_score"]
                            })
                        else:
                            failed_count += 1
                            email_reports.append({
                                "customerID": customer_id,
                                "email": customer_email,
                                "status": "Failed to Send",
                                "health_score": row["health_score"]
                            })
                    else:
                        failed_count += 1
                        email_reports.append({
                            "customerID": customer_id,
                            "email": customer_email,
                            "status": "Generation Failed",
                            "health_score": row["health_score"]
                        })

            st.session_state[f"emails_sent_{current_file_id}"] = True
            st.session_state[f"email_reports_{current_file_id}"] = email_reports

            if success_count > 0:
                st.success(f"AI Agent successfully sent {success_count} personalized retention emails.")
            if failed_count > 0:
                st.warning(f"{failed_count} emails failed to send.")

            st.markdown("#### Email Delivery Report")
            report_df = pd.DataFrame(email_reports)
            st.dataframe(report_df, use_container_width=True, hide_index=True)

        else:
            st.success("AI Agent has already sent emails for these customers.")
            st.markdown("#### Previous Email Delivery Report")
            report_df = pd.DataFrame(st.session_state[f"email_reports_{current_file_id}"])
            st.dataframe(report_df, use_container_width=True, hide_index=True)

    csv = results.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Full Predictions CSV",
        data=csv,
        file_name="health_scores.csv",
        mime="text/csv"
    )
else:
    st.info("Upload a customer CSV file to begin.")
