from datetime import datetime, timedelta
from io import BytesIO

from flask import (
    current_app, render_template, redirect, url_for, request, flash, jsonify, send_file
)
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import text

from extensions import db
from models import User, Slot, Signup
from auth import admin_required  # also registers the user_loader callback
from content import (
    ACTIVITIES, DONATION_USES, EVENTS, GALLERY, HOURS, SITE, NAV,
)
from models.chronicle import Chronicle


def img(path: str) -> str:
    return url_for("static", filename="images/" + path)

def register_routes(app):
    @app.context_processor
    def inject_globals():
        return {"site": SITE, "nav": NAV, "img": img}
    # -----------------------------------------------------------------------
    # Public / auth routes
    # -----------------------------------------------------------------------

    @app.route("/")
    def index():
        return render_template("index.html", page="index", title=None)


    @app.route("/health", methods=["GET"])
    def readiness_check():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "healthy", "database": "connected"}), 200
        # pylint: disable-next=broad-exception-caught
        except Exception:
            current_app.logger.exception("Health check failed")
            return jsonify({"status": "unhealthy", "reason": "Database unreachable"}), 503

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("signups"))

        if request.method == "POST":
            userid = request.form.get("userid", "").strip().lower()
            name = request.form.get("name", "").strip()
            password = request.form.get("password", "")
            confirm = request.form.get("confirm", "")
            current_app.logger.info("register(%s, %s)", userid, name)

            user = User.query.filter_by(userid=userid).first()

            if not user:
                flash("That user hasn't been authorized to sign up. Contact your administrator.", "danger")
            elif user.is_active:
                flash("An account already exists for that userid. Try logging in instead.", "warning")
            elif not name or not password:
                flash("Please fill in all fields.", "danger")
            elif password != confirm:
                flash("Passwords do not match.", "danger")
            elif len(password) < 8:
                flash("Password must be at least 8 characters.", "danger")
            else:
                user.name = name
                user.set_password(password)
                user.is_active = True
                db.session.commit()
                flash("Account created! You can now log in.", "success")
                return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("signups"))

        if request.method == "POST":
            userid = request.form.get("userid", "").strip().lower()
            password = request.form.get("password", "")
            user = User.query.filter_by(userid=userid).first()
            current_app.logger.info("login(%s)", userid)
            if user and not user.is_active:
                return redirect("register")
            if user and user.is_active and not user.is_deleted and user.check_password(password):
                login_user(user)
                flash(f"Welcome back, {user.name}!", "success")
                return redirect("signups")

            flash("Invalid userid or password.", "danger")

        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You've been logged out.", "info")
        return redirect(url_for("index"))

    # -----------------------------------------------------------------------
    # Regular user routes
    # -----------------------------------------------------------------------

    @app.route("/slots/<int:slot_id>/book", methods=["POST"])
    @login_required
    def book_slot(slot_id):
        slot = Slot.query.get_or_404(slot_id)
        current_app.logger.info("book_slot(%s, %s)", slot, current_user.name)

        if slot.start_time < datetime.now():
            flash("That slot is in the past.", "danger")
        elif Signup.query.filter_by(user_id=current_user.id, slot_id=slot.id).first():
            flash("You're already signed up for that slot.", "warning")
        elif slot.is_full:
            flash("Sorry, that slot just filled up.", "danger")
        else:
            db.session.add(Signup(user_id=current_user.id, slot_id=slot.id))
            db.session.commit()
            flash("You're booked!", "success")

        return redirect(url_for("signups"))

    @app.route("/slots/<int:slot_id>/cancel", methods=["POST"])
    @login_required
    def cancel_slot(slot_id):
        signup = Signup.query.filter_by(user_id=current_user.id, slot_id=slot_id).first()
        current_app.logger.info("cancel_slot(%s, %s)", slot_id, current_user.name)
        if signup:
            db.session.delete(signup)
            db.session.commit()
            flash("Booking cancelled.", "info")
        return redirect(url_for("signups"))

    # -----------------------------------------------------------------------
    # Admin routes
    # -----------------------------------------------------------------------

    @app.route("/admin_history")
    @login_required
    @admin_required
    def admin_history():
        next_week = datetime.now() + timedelta(days=7)
        slots = Slot.query.order_by(Slot.start_time.desc()).filter(Slot.start_time <= next_week)
        return render_template("admin_history.html", slots=slots)

    @app.route("/admin/authorized/add", methods=["POST"])
    @login_required
    @admin_required
    def add_user():
        userid = request.form.get("userid", "").strip().lower()
        current_app.logger.info("add_user(%s, %s)", userid)

        if not userid:
            flash("Enter a valid user.", "danger")
        elif User.query.filter_by(userid=userid).first():
            flash("That user is already on the authorized list.", "warning")
        else:
            db.session.add(User(userid=userid))
            db.session.commit()
            flash(f"{userid} is now authorized to register.", "success")

        return redirect(url_for("admin_users"))

    @app.route("/admin/user/<int:user_id>/remove", methods=["POST"])
    @login_required
    @admin_required
    def remove_user(user_id):
        user = User.query.get_or_404(user_id)

        if not user.is_active or Slot.query.filter_by(user_id=user_id).count() == 0:
            # complete delete if user is not active or doesn't have any slots
            db.session.delete(user)
        else:
            # mark deleted so history still shows user but they can't login
            user.is_deleted = True
        db.session.commit()
        flash(f"User {user.name} marked as deleted.", "info")
        return redirect(url_for("admin_users"))

    @app.route("/admin/toggle_admin/<int:user_id>", methods=["POST"])
    @login_required
    @admin_required
    def toggle_admin(user_id):
        user = User.query.get_or_404(user_id)
        user.is_admin = not user.is_admin
        db.session.commit()
        flash("Admin toggled.", "info")
        return redirect(url_for("admin_users"))


    @app.route("/admin/slots/add", methods=["POST"])
    @login_required
    @admin_required
    def add_slot():
        date_str = request.form.get("date", "")
        time_str = request.form.get("time", "")
        duration = int(request.form.get("duration", "180"))
        capacity = int(request.form.get("capacity", "5"))
        label = request.form.get("label", "").strip()
        repeat = request.form.get("repeat", None)
        end_date_str = request.form.get("end_date", "")
        current_app.logger.info(
            'add slot date: %s, time: %s, duration: %s, capacity: %s, label: %s, repeat: %s, end date: %s',
            date_str, time_str, duration, capacity, label, repeat, end_date_str
        )
        if repeat and not end_date_str:
            flash("Please provide an end_date for repeat.", "danger")
            return redirect(url_for("admin_slots"))

        try:
            start_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            make_slot(start_time, duration, capacity, label)

        except (ValueError, TypeError):
            flash("Please provide a valid date, time, duration, and capacity.", "danger")
            return redirect(url_for("admin_slots"))

        if repeat:
            if repeat == 'weekly':
                end_time = datetime.strptime(f"{end_date_str} {time_str}", "%Y-%m-%d %H:%M")
                start_time = start_time + timedelta(weeks=1)
                while start_time <= end_time:
                    try:
                        make_slot(start_time, duration, capacity, label)
                    except (ValueError, TypeError):
                        flash("Please provide a valid date, time, duration, and capacity.", "danger")
                        return redirect(url_for("admin_slots"))
                    start_time = start_time + timedelta(weeks=1)
        flash("Slot[s] created.", "success")
        return redirect(url_for("admin_slots"))

    @app.route("/admin/slots/<int:slot_id>/delete", methods=["POST"])
    @login_required
    @admin_required
    def delete_slot(slot_id):
        current_app.logger.info("delete_slot %s", slot_id)
        slot = Slot.query.get_or_404(slot_id)
        db.session.delete(slot)
        db.session.commit()
        flash("Slot deleted.", "info")
        return redirect(url_for("admin_slots"))

    @app.route("/admin/slots/<int:slot_id>")
    @login_required
    @admin_required
    def slot_detail(slot_id):
        slot = Slot.query.get_or_404(slot_id)
        return render_template("slot_detail.html", slot=slot)

    def make_slot(start_time: datetime, duration: int, capacity:int, label: str):
        if duration < 1:
            raise ValueError("duration must be at least 1")
        if capacity < 1:
            raise ValueError("capacity must be at least 1")

        db.session.add(Slot(
            start_time=start_time, duration_minutes=duration,
            capacity=capacity, label=label or None,
        ))
        db.session.commit()

    @app.route("/about")
    def about():
        return render_template("about.html", page="about", title="About Us", activities=ACTIVITIES)


    @app.route("/gallery")
    def gallery():
        return render_template("gallery.html", page="gallery", title="Gallery", photos=GALLERY)


    @app.route("/donate")
    def donate():
        return render_template("donate.html", page="donate", title="Donate", uses=DONATION_USES)


    @app.route("/calendar")
    def calendar():
        return render_template("calendar.html", page="calendar", title="Calendar")


    @app.route("/chronicles")
    def chronicles():
        items = Chronicle.query.order_by(Chronicle.date.desc()).limit(20)
        return render_template("chronicles.html", page="chronicles", title="Chronicles", items=items)


    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html", page="", title="Page not found"), 404

    @app.route('/download/<int:doc_id>')
    def download_pdf(doc_id):
        chronicle = Chronicle.query.filter_by(id=doc_id).first()
        if not chronicle:
            return not_found()
        return send_file(
            BytesIO(chronicle.data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=chronicle.filename
        )

    @app.route('/signups')
    @login_required
    def signups():
        current_app.logger.info("signups(%s)", current_user.name)
        now = datetime.now()
        two_weeks = now + timedelta(weeks=2)
        upcoming_slots = (
            Slot.query.filter(Slot.start_time >= now, Slot.start_time <= two_weeks)
            .order_by(Slot.start_time.asc())
            .all()
        )
        my_signups = {s.slot_id for s in current_user.signups}
        return render_template('bookings.html', slots=upcoming_slots, my_signups=my_signups, now=now)

    @app.route('/admin_slots')
    def admin_slots():
        now = datetime.now()
        slots = Slot.query.order_by(Slot.start_time.asc()).all()
        return render_template("admin_slots.html", slots=slots, now=now)

    @app.route('/admin_users')
    def admin_users():
        now = datetime.now()
        users = User.query.order_by(User.userid.asc()).all()
        return render_template("admin_users.html", users=users, now=now)

    @app.route('/admin_pictures')
    def admin_pictures():
        pass

    @app.route('/admin_chronicles')
    def admin_chronicles():
        pass
