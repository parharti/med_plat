from email_utils import send_reset_email

def test_send_email():
    test_email = "prishamedplat@gmail.com"  # Replace with your test email if needed
    success = send_reset_email(test_email)
    if success:
        print("✅ Email sent successfully!")
    else:
        print("❌ Failed to send email.")

if __name__ == "__main__":
    test_send_email()
