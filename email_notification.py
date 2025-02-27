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
    
    Parameters:
    submitter_name (str): Name of the person submitting the form
    submitter_email (str): Email of the person submitting the form
    skills_data (dict): Dictionary containing the skills ratings
    """
    try:
        # Check if email credentials section exists in secrets
        if "email_credentials" not in st.secrets:
            # Fall back to saving to JSON if email credentials aren't available
            return _save_submission_data(submitter_name, submitter_email, skills_data)
        
        # Get SMTP settings from Streamlit secrets
        # For Outlook.com/Hotmail
        smtp_server = "smtp.office365.com"
        smtp_port = 587
        username = st.secrets.email_credentials.sender_email
        password = st.secrets.email_credentials.sender_password
        admin_email = st.secrets.email_credentials.recipient_email  # Admin's email to receive notifications
        
        # Get expertise levels and prepare skills summary
        def get_level(value):
            if value >= 8:
                return "🔵 Primary"
            elif value >= 3:
                return "🟢 Secondary"
            elif value > 0:
                return "🟡 Limited"
            return "None"
        
        # Sort skills by value (highest to lowest) and filter out zero values
        sorted_skills = sorted(
            [(k.replace(' (Skill', '').split(')')[0], v, get_level(v)) for k, v in skills_data.items() if isinstance(v, (int, float)) and v > 0],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Create email content
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = admin_email
        msg['Subject'] = f"New Skills Matrix Submission: {submitter_name}"
        
        # HTML body for better formatting
        html_body = f"""
        <html>
        <head>
            <style>
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .primary {{
                    background-color: #e6f0ff;
                }}
                .secondary {{
                    background-color: #f0fff0;
                }}
                .limited {{
                    background-color: #fffff0;
                }}
            </style>
        </head>
        <body>
            <h2>New Skills Matrix Submission</h2>
            <p><strong>Submitted by:</strong> {submitter_name}</p>
            <p><strong>Email:</strong> {submitter_email}</p>
            <p><strong>Timestamp:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <h3>Top 10 Skills</h3>
            <table>
                <tr>
                    <th>Skill</th>
                    <th>Rating</th>
                    <th>Level</th>
                </tr>
        """
        
        # Add top 10 skills to the HTML table
        for skill, rating, level in sorted_skills[:10]:
            level_class = "primary" if "Primary" in level else "secondary" if "Secondary" in level else "limited"
            html_body += f"""
                <tr class="{level_class}">
                    <td>{skill}</td>
                    <td>{rating}</td>
                    <td>{level}</td>
                </tr>
            """
        
        html_body += """
            </table>
            
            <p>Please log in to the admin dashboard to view the complete submission.</p>
        </body>
        </html>
        """
        
        # Attach HTML body
        msg.attach(MIMEText(html_body, 'html'))
        
        # Create CSV attachment with all skills
        csv_content = "Skill,Rating,Level\n"
        for skill, rating, level in sorted_skills:
            csv_content += f'"{skill}",{rating},"{level}"\n'
        
        csv_attachment = MIMEApplication(csv_content.encode())
        csv_attachment.add_header('Content-Disposition', 'attachment', filename=f'skills_{submitter_name.replace(" ", "_")}.csv')
        msg.attach(csv_attachment)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_port == 587:
                server.starttls()  # Secure the connection for TLS
            server.login(username, password)
            server.send_message(msg)
        
        # Log successful send
        with open("email_notifications.log", "a") as log_file:
            log_file.write(f"\n[{datetime.now()}] Email notification sent to {admin_email} for submission from {submitter_name}\n")
        
        return True
        
    except Exception as e:
        # Log the error
        with open("email_notifications.log", "a") as log_file:
            log_file.write(f"\n[{datetime.now()}] ERROR sending email notification: {str(e)}\n")
        
        # Fall back to saving data to file
        return _save_submission_data(submitter_name, submitter_email, skills_data)


def _save_submission_data(submitter_name, submitter_email, skills_data):
    """
    Fallback method to save submission data when email sending fails
    """
    try:
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
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "skills": [
                {"skill": skill, "rating": rating, "level": level} 
                for skill, rating, level in sorted_skills
            ]
        }
        
        # Create directory if it doesn't exist
        os.makedirs("email_submissions", exist_ok=True)
        
        # Save the submission data to a JSON file for later email processing
        with open(os.path.join("email_submissions", log_filename), "w") as f:
            json.dump(submission_data, f, indent=2)
        
        # Log the submission information in the application for admin review
        with open("email_notifications.log", "a") as log_file:
            log_file.write(f"\n[{datetime.now()}] New submission from {submitter_name} ({submitter_email}). Data saved to {log_filename}\n")
        
        return True
    
    except Exception as e:
        st.error(f"Error processing notification: {e}")
        return False
