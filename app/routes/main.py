from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app import bcrypt, db
from app.models.patient import Patient
from app.models.doctor import Therapist
from app.models.treatment import Treatment
from app.models.assessment import Assessment
from datetime import date
from app.models.session import Session, session_doctor
import json
from sqlalchemy import func

main_bp = Blueprint('main', __name__)

def login_required_page():
    if 'user_id' not in session:
        flash('Please log in to continue.', 'danger')
        return redirect(url_for('auth.login_page'))
    return None

def admin_required_page():
    if 'user_id' not in session:
        flash('Please log in to continue.', 'danger')
        return redirect(url_for('auth.login_page'))
    if session.get('user_role') != 'admin':
        flash('Admin access only.', 'danger')
        return redirect(url_for('main.dashboard'))
    return None

@main_bp.route('/')
def index():
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
def dashboard():
    check = login_required_page()
    if check: return check
    from sqlalchemy import func, extract
    from app.models.treatment import Treatment
    from datetime import datetime

    # Date filter
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    session_query = Session.query
    if date_from:
        session_query = session_query.filter(Session.date_time >= date_from)
    if date_to:
        session_query = session_query.filter(Session.date_time <= date_to + ' 23:59:59')

    patient_count = Patient.query.count()
    therapist_count = Therapist.query.count()
    active_patients = Patient.query.filter(Patient.terminated != True).count()
    terminated_patients = Patient.query.filter(Patient.terminated == True).count()
    session_count = session_query.count()

    # Sessions per month (filtered)
    sessions_by_month = db.session.query(
        extract('year', Session.date_time).label('year'),
        extract('month', Session.date_time).label('month'),
        func.count(Session.session_id).label('count')
    )
    if date_from:
        sessions_by_month = sessions_by_month.filter(Session.date_time >= date_from)
    if date_to:
        sessions_by_month = sessions_by_month.filter(Session.date_time <= date_to + ' 23:59:59')
    sessions_by_month = sessions_by_month.group_by('year', 'month').order_by('year', 'month').all()

    months = []
    session_counts = []
    for row in sessions_by_month:
        month_name = datetime(int(row.year), int(row.month), 1).strftime('%b %Y')
        months.append(month_name)
        session_counts.append(row.count)

    # Treatment breakdown (filtered)
    treatment_query = db.session.query(
        Treatment.name,
        func.count(Session.session_id).label('count')
    ).join(Session, Session.treatment_id == Treatment.treatment_id)
    if date_from:
        treatment_query = treatment_query.filter(Session.date_time >= date_from)
    if date_to:
        treatment_query = treatment_query.filter(Session.date_time <= date_to + ' 23:59:59')
    treatment_stats = treatment_query.group_by(Treatment.name).all()

    treatment_names = [t.name for t in treatment_stats]
    treatment_counts = [t.count for t in treatment_stats]

    recent_sessions = session_query.order_by(Session.date_time.desc()).limit(5).all()

    return render_template('dashboard.html',
        patient_count=patient_count,
        therapist_count=therapist_count,
        session_count=session_count,
        active_patients=active_patients,
        terminated_patients=terminated_patients,
        months=months,
        session_counts=session_counts,
        treatment_names=treatment_names,
        treatment_counts=treatment_counts,
        recent_sessions=recent_sessions,
        date_from=date_from,
        date_to=date_to)

@main_bp.route('/patients')
def patients():
    check = login_required_page()
    if check: return check
    search = request.args.get('search', '').strip()
    if search:
        all_patients = Patient.query.filter(
            Patient.name.ilike(f'%{search}%') |
            Patient.phone.ilike(f'%{search}%')
        ).order_by(Patient.name).all()
    else:
        all_patients = Patient.query.order_by(Patient.name).all()
    return render_template('patients.html',
        patients=all_patients,
        search=search)


@main_bp.route('/patients/<int:id>/profile')
def patient_profile(id):
    check = login_required_page()
    if check: return check
    from collections import defaultdict
    from datetime import datetime
    import json

    p = Patient.query.get_or_404(id)
    assessments = Assessment.query.filter_by(patient_id=id).order_by(Assessment.date).all()
    sessions = Session.query.filter_by(patient_id=id).order_by(Session.date_time.desc()).all()
    all_treatments = Treatment.query.all()
    all_therapists = Therapist.query.order_by(Therapist.name).all()

    treatment_counts = {}
    for s in sessions:
        if s.treatment:
            name = s.treatment.name
            treatment_counts[name] = treatment_counts.get(name, 0) + 1

    brainmap = next((a for a in assessments if a.type == 'brainmap'), None)
    remaps = [a for a in assessments if a.type == 'remap']

    total_cost = sum(float(s.cost or 0) for s in sessions)
    total_discount = sum(float(s.discount or 0) for s in sessions)

    treatment_chart_data = {}
    for s in sessions:
        if not s.treatment or not s.date_time:
            continue
        name = s.treatment.name
        month = s.date_time.strftime('%b %Y')
        if name not in treatment_chart_data:
            treatment_chart_data[name] = defaultdict(int)
        treatment_chart_data[name][month] += 1

    all_months = sorted(set(
        s.date_time.strftime('%b %Y')
        for s in sessions if s.date_time
    ), key=lambda m: datetime.strptime(m, '%b %Y'))

    charts_data = []
    chart_colors = ['#1a5a58', '#C9A84C', '#7B6FAD', '#0d3b39', '#4a8a88', '#8b6914']
    for i, (treatment_name, monthly) in enumerate(treatment_chart_data.items()):
        cumulative = []
        total = 0
        for month in all_months:
            total += monthly.get(month, 0)
            cumulative.append(total)
        charts_data.append({
            'name': treatment_name,
            'color': chart_colors[i % len(chart_colors)],
            'data': cumulative,
            'total': treatment_counts.get(treatment_name, 0)
        })

    brainmap_month = brainmap.date.strftime('%b %Y') if brainmap and brainmap.date else None
    remap_months = [r.date.strftime('%b %Y') for r in remaps if r.date]

    return render_template('patient_profile.html',
        patient=p,
        assessments=assessments,
        sessions=sessions,
        treatment_counts=treatment_counts,
        brainmap=brainmap,
        remaps=remaps,
        total_cost=total_cost,
        total_discount=total_discount,
        all_months=json.dumps(all_months),
        charts_data=json.dumps(charts_data),
        brainmap_month=json.dumps(brainmap_month),
        remap_months=json.dumps(remap_months),
        all_treatments=all_treatments,
        all_therapists=all_therapists)

@main_bp.route('/sessions')
def sessions():
    check = login_required_page()
    if check: return check
    all_sessions = Session.query.order_by(Session.date_time.desc()).all()
    all_patients = Patient.query.filter(
        Patient.terminated != True).order_by(Patient.name).all()
    all_therapists = Therapist.query.order_by(Therapist.name).all()
    all_treatments = Treatment.query.all()
    preselected_patient = request.args.get('patient_id', None)
    return render_template('sessions.html',
        sessions=all_sessions,
        patients=all_patients,
        therapists=all_therapists,
        treatments=all_treatments,
        preselected_patient=preselected_patient)

@main_bp.route('/therapists')
def therapists():
    check = login_required_page()
    if check: return check
    all_therapists = Therapist.query.order_by(Therapist.name).all()
    return render_template('therapists.html', therapists=all_therapists)

# ── POST routes ──────────────────────────────────────────

@main_bp.route('/patients/add', methods=['POST'])
def add_patient_page():
    check = admin_required_page()
    if check: return check
    p = Patient(
        name=request.form.get('name'),
        dob=request.form.get('dob'),
        join_date=request.form.get('join_date') or date.today(),
        phone=request.form.get('phone'),
        address=request.form.get('address'),
        parent_name=request.form.get('parent_name'),
        terminated=request.form.get('terminated') == 'true'
    )
    db.session.add(p)
    db.session.commit()
    flash('Patient added successfully', 'success')
    return redirect(url_for('main.patients'))

@main_bp.route('/patients/edit/<int:id>', methods=['POST'])
def edit_patient_page(id):
    check = admin_required_page()
    if check: return check
    p = Patient.query.get_or_404(id)
    p.name = request.form.get('name', p.name)
    p.dob = request.form.get('dob', p.dob)
    p.phone = request.form.get('phone', p.phone)
    p.address = request.form.get('address', p.address)
    p.parent_name = request.form.get('parent_name', p.parent_name)
    p.terminated = request.form.get('terminated') == 'true'
    if p.terminated and not p.termination_date:
        p.termination_date = date.today()
    elif not p.terminated:
        p.termination_date = None
    db.session.commit()
    flash('Patient updated', 'success')
    return redirect(request.referrer or url_for('main.patients'))

@main_bp.route('/sessions/add', methods=['POST'])
def add_session_page():
    check = admin_required_page()
    if check: return check
    patient_id = request.form.get('patient_id')
    patient = Patient.query.get(patient_id)
    if patient and patient.terminated:
        flash('Cannot add session — this patient is terminated', 'danger')
        return redirect(url_for('main.sessions'))
    s = Session(
        patient_id=patient_id,
        treatment_id=request.form.get('treatment_id'),
        date_time=request.form.get('date_time'),
        cost=request.form.get('cost') or None,
        discount=request.form.get('discount') or 0,
        notes=request.form.get('notes')
    )
    for doc_id in request.form.getlist('therapist_ids'):
        therapist = Therapist.query.get(doc_id)
        if therapist:
            s.doctors.append(therapist)
    db.session.add(s)
    db.session.commit()
    flash('Session added', 'success')
    # Redirect back to patient profile if came from there
    referrer = request.referrer
    if referrer and 'profile' in referrer:
        return redirect(url_for('main.patient_profile', id=patient_id))
    return redirect(url_for('main.sessions'))

@main_bp.route('/sessions/edit/<int:id>', methods=['POST'])
def edit_session_page(id):
    check = admin_required_page()
    if check: return check
    s = Session.query.get_or_404(id)
    s.patient_id = request.form.get('patient_id', s.patient_id)
    s.treatment_id = request.form.get('treatment_id', s.treatment_id)
    s.date_time = request.form.get('date_time', s.date_time)
    s.cost = request.form.get('cost') or None
    s.discount = request.form.get('discount') or 0
    s.notes = request.form.get('notes', s.notes)
    if request.form.getlist('therapist_ids'):
        s.doctors = []
        for doc_id in request.form.getlist('therapist_ids'):
            therapist = Therapist.query.get(doc_id)
            if therapist:
                s.doctors.append(therapist)
    db.session.commit()
    flash('Session updated', 'success')
    return redirect(request.referrer or url_for('main.sessions'))

@main_bp.route('/sessions/delete/<int:id>', methods=['POST'])
def delete_session_page(id):
    check = admin_required_page()
    if check: return check
    s = Session.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    flash('Session deleted', 'success')
    return redirect(request.referrer or url_for('main.sessions'))

@main_bp.route('/therapists/add', methods=['POST'])
def add_therapist_page():
    check = admin_required_page()
    if check: return check
    import uuid
    email = request.form.get('email') or f"therapist_{uuid.uuid4().hex[:8]}@touchbrain.local"
    t = Therapist(
        name=request.form.get('name'),
        email=email,
        phone=request.form.get('phone'),
        password_hash=bcrypt.generate_password_hash('password123').decode('utf-8'),
        role='admin',
        join_date=request.form.get('join_date') or date.today()
    )
    db.session.add(t)
    db.session.commit()
    flash('Therapist added', 'success')
    return redirect(url_for('main.therapists'))

@main_bp.route('/therapists/edit/<int:id>', methods=['POST'])
def edit_therapist_page(id):
    check = admin_required_page()
    if check: return check
    t = Therapist.query.get_or_404(id)
    t.name = request.form.get('name', t.name)
    t.email = request.form.get('email', t.email)
    t.phone = request.form.get('phone', t.phone)
    if request.form.get('termination_date'):
        t.termination_date = request.form.get('termination_date')
    db.session.commit()
    flash('Therapist updated', 'success')
    return redirect(url_for('main.therapists'))

@main_bp.route('/patients/<int:id>/assessment/add', methods=['POST'])
def add_assessment_page(id):
    check = admin_required_page()
    if check: return check
    a = Assessment(
        patient_id=id,
        type=request.form.get('type'),
        date=request.form.get('date') or date.today(),
        notes=request.form.get('notes')
    )
    db.session.add(a)
    db.session.commit()
    flash('Assessment added', 'success')
    return redirect(url_for('main.patient_profile', id=id))

@main_bp.route('/treatments')
def treatments():
    check = admin_required_page()
    if check: return check
    from app.models.treatment import Treatment
    all_treatments = Treatment.query.order_by(Treatment.name).all()
    return render_template('treatments.html', treatments=all_treatments)

@main_bp.route('/treatments/add', methods=['POST'])
def add_treatment_page():
    check = admin_required_page()
    if check: return check
    from app.models.treatment import Treatment
    name = request.form.get('name', '').strip()
    if not name:
        flash('Treatment name is required', 'danger')
        return redirect(url_for('main.treatments'))
    existing = Treatment.query.filter_by(name=name).first()
    if existing:
        flash('Treatment already exists', 'danger')
        return redirect(url_for('main.treatments'))
    t = Treatment(name=name)
    db.session.add(t)
    db.session.commit()
    flash('Treatment added', 'success')
    return redirect(url_for('main.treatments'))

@main_bp.route('/treatments/edit/<int:id>', methods=['POST'])
def edit_treatment_page(id):
    check = admin_required_page()
    if check: return check
    from app.models.treatment import Treatment
    t = Treatment.query.get_or_404(id)
    name = request.form.get('name', '').strip()
    if not name:
        flash('Treatment name is required', 'danger')
        return redirect(url_for('main.treatments'))
    t.name = name
    db.session.commit()
    flash('Treatment updated', 'success')
    return redirect(url_for('main.treatments'))

@main_bp.route('/treatments/delete/<int:id>', methods=['POST'])
def delete_treatment_page(id):
    check = admin_required_page()
    if check: return check
    from app.models.treatment import Treatment
    t = Treatment.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    flash('Treatment deleted', 'success')
    return redirect(url_for('main.treatments'))

@main_bp.route('/users')
def users():
    check = admin_required_page()
    if check: return check
    from app.models.user import User
    all_users = User.query.order_by(User.name).all()
    return render_template('users.html', users=all_users)

@main_bp.route('/users/add', methods=['POST'])
def add_user_page():
    check = admin_required_page()
    if check: return check
    from app.models.user import User
    import uuid
    email = request.form.get('email', '').strip()
    if not email:
        email = f"user_{uuid.uuid4().hex[:8]}@touchbrain.local"
    u = User(
        name=request.form.get('name'),
        email=email,
        password_hash=bcrypt.generate_password_hash(
            request.form.get('password')).decode('utf-8'),
        role=request.form.get('role', 'staff'),
        join_date=date.today(),
        active=True
    )
    db.session.add(u)
    db.session.commit()
    flash('User added', 'success')
    return redirect(url_for('main.users'))

@main_bp.route('/users/edit/<int:id>', methods=['POST'])
def edit_user_page(id):
    check = admin_required_page()
    if check: return check
    from app.models.user import User
    u = User.query.get_or_404(id)
    u.name = request.form.get('name', u.name)
    u.role = request.form.get('role', u.role)
    u.active = request.form.get('active') == 'true'
    if request.form.get('password'):
        u.password_hash = bcrypt.generate_password_hash(
            request.form.get('password')).decode('utf-8')
    db.session.commit()
    flash('User updated', 'success')
    return redirect(url_for('main.users'))

@main_bp.route('/patients/<int:id>/print')
def print_patient(id):
    check = login_required_page()
    if check: return check
    from datetime import datetime

    p = Patient.query.get_or_404(id)
    assessments = Assessment.query.filter_by(patient_id=id).order_by(Assessment.date).all()
    sessions = Session.query.filter_by(patient_id=id).order_by(Session.date_time.asc()).all()

    treatment_counts = {}
    for s in sessions:
        if s.treatment:
            name = s.treatment.name
            treatment_counts[name] = treatment_counts.get(name, 0) + 1

    brainmap = next((a for a in assessments if a.type == 'brainmap'), None)
    remaps = [a for a in assessments if a.type == 'remap']

    return render_template('print_patient.html',
        patient=p,
        assessments=assessments,
        sessions=sessions,
        treatment_counts=treatment_counts,
        brainmap=brainmap,
        remaps=remaps,
        now=datetime.now().strftime('%B %d, %Y'))