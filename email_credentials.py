"""
This script securely saves your email credentials for Prefect notifications.

- Use an email address
- Generate an App Password for this script (DO NOT use your email password)
- Run this script ONCE locally:
    python setup_email_credentials.py
"""

from prefect_email import EmailServerCredentials

# UPDATE THESE WITH YOUR OWN INFO
your_email = "youremail@gmail.com"         # Your email address
your_app_password = "your_app_password"    # Use an App Password, NOT your email password

# Save credentials securely to Prefect's local block store
credentials = EmailServerCredentials(
    username=your_email,
    password=your_app_password
)

# Saves under the name "gmail-creds" — used in the ETL script
credentials.save("gmail-creds", overwrite=True)

print("Email credentials saved successfully under 'gmail-creds'.")
print("You can now receive flow failure alerts via email.")
