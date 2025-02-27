import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pandas as pd
import streamlit as st

def send_notification_email(submitter_name, submitter_email, skills_data):
    """
    Send notification email to admin when a new skills matrix is submitted
    
    Parameters:
    submitter_name (str): Name of the person submitting the form
    submitter_email (str): Email of the person submitting the form
    skills_data (dict): Dictionary containing the skills ratings
    """
    try:
        # Email configuration - using hardcoded values as specified
        email_sender = "ankitamadanavadhani@outlook.com"
        email_password = "Solomon123!"
        email_recipient = "aavadhani@brieflylegal.com"
        
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = email_recipient
        msg['Subject'] = f"New Skills Matrix Submission: {submitter_name}"
        
        # Create email body with submission info
        email_body = f"""
        <html>
        <body>
        <h2>New Skills Matrix Submission</h2>
        <p><strong>Name:</strong> {submitter_name}</p>
        <p><strong>Email:</strong> {submitter_email}</p>
        <p><strong>Submission Time:</strong> {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <h3>Skills Overview:</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse;">
        <tr>
            <th>Skill</th>
            <th>Rating</th>
            <th>Level</th>
        </tr>
        """
        
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
            [(k.replace(' (Skill', '').split(')')[0], v) for k, v in skills_data.items() if isinstance(v, (int, float)) and v > 0],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Add all skills with values > 0 to the email
        for skill_name, value in sorted_skills:
            level = get_level(value)
            email_body += f"""
            <tr>
                <td>{skill_name}</td>
                <td>{value}</td>
                <td>{level}</td>
            </tr>
            """
        
        email_body += """
        </table>
        <p>Please check the admin dashboard for complete details.</p>
        </body>
        </html>
        """
        
        # Attach the email body
        msg.attach(MIMEText(email_body, 'html'))
        
        # Send the email using Outlook SMTP server
        with smtplib.SMTP('smtp-mail.outlook.com', 587) as smtp:
            smtp.starttls()  # Outlook uses TLS
            smtp.login(email_sender, email_password)
            smtp.send_message(msg)
        
        return True
    
    except Exception as e:
        st.error(f"Error sending notification email: {e}")
        return False
