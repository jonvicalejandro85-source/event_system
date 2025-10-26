from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_file
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from config import Config
from models import db, Event, Attendee
from forms import EventForm, RegisterForm
from notifications import init_mail, send_rsvp_email
from io import StringIO
from io import BytesIO 
from datetime import datetime
import csv
from flask import send_file

import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    init_mail(app)

    with app.app_context():
        db.create_all()

    # ---------------- Home / events list ----------------
    @app.route("/")
    def index():
        events = Event.query.order_by(Event.start_datetime.desc()).all()
        return render_template("index.html", events=events)

    # ---------------- Create new event ----------------
    @app.route("/events/new", methods=["GET", "POST"])
    def create_event():
        form = EventForm()
        if form.validate_on_submit():
            start_datetime = datetime.combine(form.start_date.data, form.start_time.data)
            end_datetime = None
            if form.end_date.data and form.end_time.data:
                end_datetime = datetime.combine(form.end_date.data, form.end_time.data)

            ev = Event(
                name=form.name.data,
                description=form.description.data,
                venue=form.venue.data,
                start_datetime=start_datetime,
                end_datetime=end_datetime
            )
            db.session.add(ev)
            db.session.commit()
            flash("Event created successfully.", "success")
            return redirect(url_for('index'))
        return render_template("event_form.html", form=form, action="Create")

    # ---------------- Edit event ----------------
    @app.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
    def edit_event(event_id):
        ev = Event.query.get_or_404(event_id)
        form = EventForm(
            name=ev.name,
            description=ev.description,
            venue=ev.venue,
            start_date=ev.start_datetime.date(),
            start_time=ev.start_datetime.time(),
            end_date=ev.end_datetime.date() if ev.end_datetime else None,
            end_time=ev.end_datetime.time() if ev.end_datetime else None
        )

        if form.validate_on_submit():
            ev.name = form.name.data
            ev.description = form.description.data
            ev.venue = form.venue.data
            ev.start_datetime = datetime.combine(form.start_date.data, form.start_time.data)
            if form.end_date.data and form.end_time.data:
                ev.end_datetime = datetime.combine(form.end_date.data, form.end_time.data)
            else:
                ev.end_datetime = None

            db.session.commit()
            flash("Event updated successfully.", "success")
            return redirect(url_for('event_detail', event_id=event_id))

        return render_template("event_form.html", form=form, action="Edit")

    # ---------------- Event detail + attendees ----------------
    @app.route("/events/<int:event_id>")
    def event_detail(event_id):
        ev = Event.query.get_or_404(event_id)
        form = RegisterForm()
        return render_template("event_detail.html", event=ev, form=form)

    # ---------------- Register (RSVP) ----------------
    @app.route("/events/<int:event_id>/register", methods=["POST"])
    def register(event_id):
        ev = Event.query.get_or_404(event_id)
        form = RegisterForm()
        if form.validate_on_submit():
            att = Attendee(
                event=ev,
                full_name=form.full_name.data,
                email=form.email.data,
                rsvp_status='registered'
            )
            db.session.add(att)
            db.session.commit()

            # send email (if provided)
            if att.email:
                html = render_template("emails/rsvp_email.html", attendee=att, event=ev)
                send_rsvp_email(app, att.email, f"Registration confirmed: {ev.name}", html)

            flash("Thanks for registering!", "success")
        else:
            flash("Invalid registration data.", "danger")
        return redirect(url_for('event_detail', event_id=event_id))

    # ---------------- Notify attendees ----------------
    @app.route("/events/<int:event_id>/notify", methods=["POST"])
    def notify(event_id):
        ev = Event.query.get_or_404(event_id)
        subject = request.form.get('subject') or f"Update about {ev.name}"
        message = request.form.get('message') or ''
        for att in ev.attendees:
            if att.email:
                html = f"<p>Hi {att.full_name},</p><p>{message}</p>"
                send_rsvp_email(app, att.email, subject, html)
        flash("Notifications sent (if configured).", "info")
        return redirect(url_for('event_detail', event_id=event_id))

    # ---------------- Dashboard ----------------
    @app.route("/dashboard")
    def dashboard():
        events = Event.query.order_by(Event.start_datetime.desc()).all()
        data = []
        for ev in events:
            total = len(ev.attendees)
            attended = len([a for a in ev.attendees if a.rsvp_status == 'attended'])
            data.append({
                'id': ev.id, 'name': ev.name, 'total': total, 'attended': attended
            })
        return render_template("dashboard.html", events=events, data=data)

    # ---------------- Export attendees CSV ----------------
    @app.route("/events/<int:event_id>/export")
    def export_attendees(event_id):
        ev = Event.query.get_or_404(event_id)
        attendees = Attendee.query.filter_by(event_id=event_id).all()

        # Create CSV content in memory
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Name", "Email"])  # CSV headers

        for attendee in attendees:
            writer.writerow([attendee.name, attendee.email])

        # Convert StringIO text to BytesIO for Flask send_file
        mem = BytesIO()
        mem.write(output.getvalue().encode('utf-8'))
        mem.seek(0)
        output.close()

        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"{ev.name}_attendees.csv"
        )

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)