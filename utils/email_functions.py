from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_verification_email(user, verification_link):
    subject = 'Verify your account on TechyCart'
    from_email = f"TechyCart <{settings.DEFAULT_FROM_EMAIL}>"
    to_email = [user.email]

    # Plain text version (for fallback)
    text_content = f"""
Hi {user.first_name},

Please verify your account by clicking the link below:
{verification_link}

Thank you for using TechyCart!
"""

    # HTML email content
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Verify Your Email</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 40px;">
  <div style="max-width: 600px; margin: auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0px 2px 8px rgba(0,0,0,0.1);">
    <h2 style="color: #333;">Hi {user.first_name},</h2>
    <p style="font-size: 16px;">Welcome to <strong>TechyCart</strong>! Please verify your email address by clicking the button below:</p>
    <p style="text-align: center; margin: 30px 0;">
      <a href="{verification_link}" style="background-color: #28a745; color: #fff; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-size: 16px;">Verify Email</a>
    </p>
    <p style="font-size: 14px; color: #888;">If you didn’t sign up, you can safely ignore this email.</p>
    <p style="margin-top: 40px; font-size: 14px;">— The TechyCart Team</p>
  </div>
</body>
</html>
"""

    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
