import pandas as pd
import numpy as np

np.random.seed(41)
n = 20  # number of fake users

# Example complaint categories
complaints = [
    "Frequent call drops and poor voice clarity",
    "Internet speed is too slow during peak hours",
    "Billing issue: charged twice this month",
    "Customer support didn’t resolve my issue",
    "Frequent disconnections in internet service",
    "Plan renewal failed despite payment",
    "Network coverage is poor in my area",
    "High latency during video streaming",
    "Unable to log in to customer portal",
    "Received incorrect bill amount"
]

# Generate dataset
test_data = pd.DataFrame({
    "customerID": [f"{i:04d}-TEST" for i in range(1, n + 1)],
    "gender": np.random.choice(["Male", "Female"], n),
    "SeniorCitizen": np.random.choice([0, 1], n),
    "Partner": np.random.choice(["Yes", "No"], n),
    "Dependents": np.random.choice(["Yes", "No"], n),
    "tenure": np.random.randint(1, 72, n),
    "PhoneService": np.random.choice(["Yes", "No"], n),
    "MultipleLines": np.random.choice(["Yes", "No", "No phone service"], n),
    "InternetService": np.random.choice(["DSL", "Fiber optic", "No"], n),
    "OnlineSecurity": np.random.choice(["Yes", "No", "No internet service"], n),
    "OnlineBackup": np.random.choice(["Yes", "No", "No internet service"], n),
    "DeviceProtection": np.random.choice(["Yes", "No", "No internet service"], n),
    "TechSupport": np.random.choice(["Yes", "No", "No internet service"], n),
    "StreamingTV": np.random.choice(["Yes", "No", "No internet service"], n),
    "StreamingMovies": np.random.choice(["Yes", "No", "No internet service"], n),
    "Contract": np.random.choice(["Month-to-month", "One year", "Two year"], n),
    "PaperlessBilling": np.random.choice(["Yes", "No"], n),
    "PaymentMethod": np.random.choice(
        ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
        n
    ),
    "MonthlyCharges": np.random.uniform(20, 120, n),
    "TotalCharges": np.random.uniform(100, 8000, n),
})

# Add email and complaint columns
test_data["email"] = test_data["customerID"].apply(
    lambda x: f"{x.lower().replace('-test', '')}@telecommail.com"
)
test_data["complaint"] = np.random.choice(complaints, n)

# Save CSV
test_data.to_csv("test_customers.csv", index=False)
print("✅ Generated test_customers.csv with emails and complaints successfully!")
