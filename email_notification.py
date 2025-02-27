import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pandas as pd
import streamlit as st
import json
import os
from datetime import datetime

def send_notification_email(submitter_name, submitter_email, skills_data):
    """
    Send email notification about new skill matrix submission
    """
    try:
        # For Outlook.com/Hotmail
        smtp_server = "smtp.office365.com"
        smtp_port = 587
        username = st.secrets.email_credentials.sender_email
        password = st.secrets.email_credentials.sender_password
        recipient_email = st.secrets.email_credentials.recipient_email
        
        # Get expertise levels and prepare skills summary
        def get_level(value):
            if value >= 8:
                return "Primary"
            elif value >= 3:
                return "Secondary"
            elif value > 0:
                return "Limited"
            return "None"
        
        # Sort skills by value (highest to lowest) and filter out zero values
        sorted_skills = []
        for k, v in skills_data.items():
            if isinstance(v, (int, float)) and v > 0:
                skill_name = k.replace(' (Skill', '').split(')')[0]
                sorted_skills.append((skill_name, v, get_level(v)))
        
        sorted_skills.sort(key=lambda x: x[1], reverse=True)
        
        # Create email content
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = recipient_email
        msg['Subject'] = f"New Skills Matrix Submission: {submitter_name}"
        
        # Plain text email body (simpler than HTML for better delivery)
        email_body = f"""
New Skills Matrix Submission

Submitted by: {submitter_name}
Email: {submitter_email}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Top 10 Skills:
"""
        
        # Add top skills to the email
        for i, (skill, rating, level) in enumerate(sorted_skills[:10], 1):
            email_body += f"{i}. {skill}: {rating} points ({level})\n"
            
        email_body += "\nPlease check the admin dashboard for complete details."
        
        # Attach text body
        msg.attach(MIMEText(email_body, 'plain'))
        
        # Create CSV attachment with all skills
        csv_content = "Skill,Rating,Level\n"
        for skill, rating, level in sorted_skills:
            csv_content += f'"{skill}",{rating},"{level}"\n'
        
        csv_attachment = MIMEApplication(csv_content.encode())
        csv_attachment.add_header('Content-Disposition', 'attachment', 
                                 filename=f'skills_{submitter_name.replace(" ", "_")}.csv')
        msg.attach(csv_attachment)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(username, password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        # Fall back to saving data to file
        print(f"Email error: {e}")
        return _save_submission_data(submitter_name, submitter_email, skills_data)


def _save_submission_data(submitter_name, submitter_email, skills_data):
    """
    Fallback method to save submission data when email sending fails
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs("email_submissions", exist_ok=True)
        
        # Create a timestamped log file with the submission data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"submission_{timestamp}_{submitter_name.replace(' ', '_')}.json"
        
        # Get expertise levels
        def get_level(value):
            if value >= 8:
                return "Primary"
            elif value >= 3:
                return "Secondary"
            elif value > 0:
                return "Limited"
            return "None"
        
        # Sort skills by value (highest to lowest)
        sorted_skills = []
        for k, v in skills_data.items():
            if isinstance(v, (int, float)) and v > 0:
                skill_name = k.replace(' (Skill', '').split(')')[0]
                sorted_skills.append({"skill": skill_name, "rating": v, "level": get_level(v)})
        
        sorted_skills.sort(key=lambda x: x["rating"], reverse=True)
        
        # Create a structured format for the submission data
        submission_data = {
            "submission_info": {
                "name": submitter_name,
                "email": submitter_email,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "skills": sorted_skills
        }
        
        # Save the submission data to a JSON file for later email processing
        file_path = os.path.join("email_submissions", log_filename)
        with open(file_path, "w") as f:
            json.dump(submission_data, f, indent=2)
        
        print(f"Saved submission to {file_path}")
        return True
    
    except Exception as e:
        print(f"Error saving submission data: {e}")
        return False
