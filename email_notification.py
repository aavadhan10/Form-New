import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import streamlit as st

def send_notification_email(submitter_name, submitter_email, skills_data):
    """
    Send email notification about new skill matrix submission
    
    Args:
        submitter_name (str): Name of the person who submitted the form
        submitter_email (str): Email of the person who submitted the form
        skills_data (dict): Dictionary containing the skills data submitted
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Get email configuration from Streamlit secrets
        smtp_server = st.secrets.get("email_smtp_server", "smtp.office365.com")
        smtp_port = st.secrets.get("email_smtp_port", 587)
        username = st.secrets.get("email_username", "")
        password = st.secrets.get("email_password", "")
        recipient_email = st.secrets.get("admin_email", "")
        
        # Validate email configuration
        if not all([smtp_server, smtp_port, username, password, recipient_email]):
            print("Email configuration incomplete. Check Streamlit secrets.")
            return False
            
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = recipient_email
        msg['Subject'] = f"New Skills Matrix Submission: {submitter_name}"
        
        # Create message body with HTML formatting
        # Get top skills (values >= 8)
        primary_skills = [(k.replace(' (Skill', '').split(')')[0], v) 
                         for k, v in skills_data.items() 
                         if isinstance(v, (int, float)) and v >= 8]
        primary_skills = sorted(primary_skills, key=lambda x: x[1], reverse=True)
        
        # Get secondary skills (values 3-7)
        secondary_skills = [(k.replace(' (Skill', '').split(')')[0], v) 
                           for k, v in skills_data.items() 
                           if isinstance(v, (int, float)) and 3 <= v < 8]
        secondary_skills = sorted(secondary_skills, key=lambda x: x[1], reverse=True)[:5]  # Top 5
        
        # Format message body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>New Skills Matrix Submission</h2>
            <p>A new skills matrix has been submitted with the following details:</p>
            
            <table style="border-collapse: collapse; width: 100%;">
                <tr>
                    <td style="padding: 8px; width: 200px;"><strong>Name:</strong></td>
                    <td style="padding: 8px;">{submitter_name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><strong>Email:</strong></td>
                    <td style="padding: 8px;"><a href="mailto:{submitter_email}">{submitter_email}</a></td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><strong>Timestamp:</strong></td>
                    <td style="padding: 8px;">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</td>
                </tr>
            </table>
            
            <h3>Primary Areas of Expertise:</h3>
            <ul>
        """
        
        # Add primary skills to the email
        if primary_skills:
            for skill, value in primary_skills:
                body += f"<li><strong>{skill}:</strong> {value} points</li>"
        else:
            body += "<li>No primary skills (8+ points) identified</li>"
            
        body += """
            </ul>
            
            <h3>Top Secondary Skills:</h3>
            <ul>
        """
        
        # Add secondary skills to the email
        if secondary_skills:
            for skill, value in secondary_skills:
                body += f"<li><strong>{skill}:</strong> {value} points</li>"
        else:
            body += "<li>No secondary skills (3-7 points) identified</li>"
            
        body += """
            </ul>
            
            <p>Please check the admin dashboard for complete details.</p>
            <p><a href="https://your-streamlit-app-url/">Access Admin Dashboard</a></p>
        </body>
        </html>
        """
        
        # Attach HTML part
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to server with error handling and proper timeout
        try:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.ehlo()
            
            # Check if TLS is supported
            if server.has_extn('STARTTLS'):
                server.starttls()
                server.ehlo()  # Re-identify ourselves over TLS connection
            
            server.login(username, password)
            server.sendmail(username, recipient_email, msg.as_string())
            server.quit()
            print("Email notification sent successfully")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("SMTP Authentication Error: Invalid username or password")
        except smtplib.SMTPConnectError:
            print("SMTP Connection Error: Failed to connect to the server")
        except smtplib.SMTPServerDisconnected:
            print("Server unexpectedly disconnected")
        except smtplib.SMTPException as e:
            print(f"SMTP Error: {str(e)}")
        
        return False
        
    except Exception as e:
        # Save failure details to file for debugging
        try:
            os.makedirs("email_failures", exist_ok=True)
            failure_file = os.path.join("email_failures", f"email_failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
            with open(failure_file, "w") as f:
                f.write(f"Error sending email notification for: {submitter_name} ({submitter_email})\n")
                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Error: {type(e).__name__}: {str(e)}\n\n")
                
                # Include the skills data for debugging
                f.write("Skills Data:\n")
                for skill, value in sorted([(k, v) for k, v in skills_data.items() if v > 0], 
                                         key=lambda x: x[1], reverse=True):
                    f.write(f"- {skill}: {value}\n")
                
            print(f"Email failure logged to: {failure_file}")
        except Exception as log_error:
            print(f"Failed to save error log: {log_error}")
        
        return False

# For testing outside of Streamlit environment
if __name__ == "__main__":
    # Simulate sample data
    test_skills = {
        'Python (Skill 1)': 9,
        'Data Analysis (Skill 2)': 8,
        'Project Management (Skill 3)': 7,
        'Communication (Skill 4)': 6
    }
    
    # Test the function
    success = send_notification_email("Test User", "test@example.com", test_skills)
    print(f"Email test result: {'Success' if success else 'Failed'}")
