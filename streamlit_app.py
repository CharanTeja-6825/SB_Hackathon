import streamlit as st
import pandas as pd
import joblib
import requests

# ================================
# 🎯 Load model and encoder
# ================================
@st.cache_resource
def load_assets():
    model = joblib.load("model.pkl")
    label_encoder = joblib.load("label_encoder.pkl")
    return model, label_encoder

model, label_encoder = load_assets()

# ================================
# 🧠 Helper: predict churn & health score
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
# ⚙️ Helper: send data to n8n webhook
# ================================
def send_to_n8n(top_5_df, webhook_url):
    success, fail = 0, 0
    for _, row in top_5_df.iterrows():
        payload = {
            "customer_id": row.get("customerID", ""),
            "email": row.get("email", f"{row['customerID'].lower()}@telecommail.com"),
            "issue": row.get("complaint", "General dissatisfaction"),
            "health_score": float(row.get("health_score", 0))
        }
        try:
            r = requests.post(webhook_url, json=payload, timeout=10)
            if r.status_code == 200:
                success += 1
            else:
                fail += 1
        except Exception as e:
            fail += 1
            print(f"Error sending to n8n: {e}")
    return success, fail

# ================================
# 🖥️ Streamlit UI
# ================================
st.set_page_config(page_title="Telecom SMB Churn Health Dashboard", layout="centered")

st.title("📊 Telecom SMB Customer Health Dashboard")
st.caption("Predict churn risk and trigger retention automation through n8n")

uploaded_file = st.file_uploader("📂 Upload your customer CSV", type=["csv"])
webhook_url = st.text_input("🔗 n8n Webhook URL", placeholder="https://your-n8n-instance/webhook/notify")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"✅ File uploaded: {uploaded_file.name}")

    with st.spinner("Analyzing customer data..."):
        results = predict_health_scores(df)

    top_5 = results.sort_values("health_score").head(5)
    st.subheader("🚨 Top 5 High-Risk Customers")
    st.dataframe(
        top_5[["customerID", "email", "complaint", "health_score", "Risk_Level"]]
        .style.background_gradient(cmap="Reds", subset=["health_score"])
        .format({"health_score": "{:.3f}"})
    )

    st.markdown("### ⚡ Automation")
    if st.button("Send to n8n Automation"):
        if webhook_url.strip() == "":
            st.error("Please enter your n8n Webhook URL first.")
        else:
            with st.spinner("Sending data to n8n..."):
                success, fail = send_to_n8n(top_5, webhook_url)
            st.success(f"✅ Sent {success} users to n8n | ❌ Failed: {fail}")

    # Download predictions
    csv = results.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Full Predictions CSV",
        data=csv,
        file_name="health_scores.csv",
        mime="text/csv"
    )
else:
    st.info("👆 Upload a customer CSV file to begin.")

st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>Built with ❤️ • AI + Automation • n8n Integration</p>",
    unsafe_allow_html=True,
)
