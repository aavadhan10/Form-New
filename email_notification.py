import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import streamlit as st
import json

def send_notification_email(submitter_name, submitter_email, skills_data):
    """
    Alternative approach to save submission data for later email processing
    
    Parameters:
    submitter_name (str): Name of the person submitting the form
    submitter_email (str): Email of the person submitting the form
    skills_data (dict): Dictionary containing the skills ratings
    """
    try:
        # Create a timestamped log file with the submission data
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
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
        sorted_skills = sorted(
            [(k.replace(' (Skill', '').split(')')[0], v, get_level(v)) for k, v in skills_data.items() if isinstance(v, (int, float)) and v > 0],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Create a structured format for the submission data
        submission_data = {
            "submission_info": {
                "name": submitter_name,
                "email": submitter_email,
                "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "skills": [
                {"skill": skill, "rating": rating, "level": level} 
                for skill, rating, level in sorted_skills
            ]
        }
        
        # Save the submission data to a JSON file for later email processing
        with open(log_filename, "w") as f:
            json.dump(submission_data, f, indent=2)
        
        # Log the submission information in the application for admin review
        with open("email_notifications.log", "a") as log_file:
            log_file.write(f"\n[{pd.Timestamp.now()}] New submission from {submitter_name} ({submitter_email}). Data saved to {log_filename}\n")
        
        st.info(f"Note: Due to email security restrictions, submission details have been saved to {log_filename} for manual email delivery.")
        return True
    
    except Exception as e:
        st.error(f"Error processing notification: {e}")
        return False
