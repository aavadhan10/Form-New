import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import streamlit as st
import json
import os
from datetime import datetime

def send_notification_email(submitter_name, submitter_email, skills_data):
    """
    Send email notification about new skill matrix submission
    Using a simpler approach with explicit error handling
    """
    try:
        # Hard-code the values instead of reading from secrets
        # MODIFY THESE VALUES
        smtp_server = "smtp.office365.com"
        smtp_port = 587
        username = "ankitamadanavadhani@outlook.com"  # Your email
        password = "Solomon123!"  # Your password
        recipient_email = "ankitamadanavadhani@outlook.com"  # Where to send notifications
        
        # Print debug information
        print(f"SMTP Server: {smtp_server}")
        print(f"SMTP Port: {smtp_port}")
        print(f"Username: {username}")
        print(f"Recipient: {recipient_email}")
        
        # Create a simple plain-text message
        message = f"""
Subject: New Skills Matrix Submission: {submitter_name}

A new skills matrix has been submitted:

Name: {submitter_name}
Email: {submitter_email}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Please check the admin dashboard for complete details.
"""
        
        # Connect to server and send email
        print("Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()  # Can help with some servers
        print("Starting TLS...")
        server.starttls()
        print("Logging in...")
        server.login(username, password)
        print("Sending email...")
        server.sendmail(username, recipient_email, message)
        print("Closing connection...")
        server.quit()
        
        print("Email sent successfully!")
        return True
        
    except Exception as e:
        # Print detailed error information
        print(f"Email sending failed with error: {type(e).__name__}: {str(e)}")
        
        # Save submission data to file as backup
        try:
            os.makedirs("email_failures", exist_ok=True)
            failure_file = os.path.join("email_failures", f"submission_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{submitter_name.replace(' ', '_')}.txt")
            
            with open(failure_file, "w") as f:
                f.write(f"Submission from: {submitter_name} ({submitter_email})\n")
                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Email Error: {str(e)}\n\n")
                
                # Write top skills
                f.write("Top Skills:\n")
                for skill, value in sorted([(k, v) for k, v in skills_data.items() if v > 0], key=lambda x: x[1], reverse=True)[:10]:
                    skill_name = skill.replace(' (Skill', '').split(')')[0]
                    f.write(f"- {skill_name}: {value}\n")
            
            print(f"Saved failure log to {failure_file}")
        except Exception as log_error:
            print(f"Failed to save error log: {log_error}")
        
        return False
