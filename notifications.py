from flask_mail import Message, Mail

mail = Mail()

def init_mail(app):
    mail.init_app(app)

def send_rsvp_email(app, to_email, subject, html_body):
    if not app.config.get('MAIL_SERVER'):
        app.logger.warning("Mail server not configured; skipping email.")
        return False

    # Use MAIL_DEFAULT_SENDER or MAIL_USERNAME as fallback
    sender = app.config.get('MAIL_DEFAULT_SENDER') or app.config.get('MAIL_USERNAME')
    if not sender:
        app.logger.warning("Mail sender not configured; skipping email.")
        return False

    with app.app_context():
        try:
            msg = Message(
                subject=subject,
                sender=sender,
                recipients=[to_email],
                html=html_body
            )
            mail.send(msg)
            app.logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            # Print/log detailed error for debugging
            app.logger.error(f"Failed to send email to {to_email}: {e}")
            print(f"Failed to send email to {to_email}: {e}")
            return False
