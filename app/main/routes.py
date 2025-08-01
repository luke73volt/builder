from flask import render_template, flash, redirect, url_for
from app import db
from app.main import bp
from app.main.forms import MedicationForm, LoadUnloadForm, ReportForm
from app.models import Medication, Transaction
from flask_login import login_required, current_user
from app.decorators import role_required

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    low_stock_meds = Medication.query.filter(Medication.quantity <= Medication.min_stock_level).all()
    return render_template('index.html', title='Home', low_stock_meds=low_stock_meds)

@bp.route('/medications')
@login_required
def medications():
    meds = Medication.query.all()
    return render_template('medications.html', medications=meds)

@bp.route('/add_medication', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_medication():
    form = MedicationForm()
    if form.validate_on_submit():
        med = Medication(name=form.name.data, description=form.description.data,
                         quantity=form.quantity.data, min_stock_level=form.min_stock_level.data)
        db.session.add(med)
        db.session.commit()
        flash('Medication added successfully.')
        return redirect(url_for('main.medications'))
    return render_template('add_medication.html', title='Add Medication', form=form)

@bp.route('/edit_medication/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_medication(id):
    med = Medication.query.get_or_404(id)
    form = MedicationForm(obj=med)
    if form.validate_on_submit():
        med.name = form.name.data
        med.description = form.description.data
        med.quantity = form.quantity.data
        med.min_stock_level = form.min_stock_level.data
        db.session.commit()
        flash('Medication updated successfully.')
        return redirect(url_for('main.medications'))
    return render_template('edit_medication.html', title='Edit Medication', form=form)

@bp.route('/delete_medication/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_medication(id):
    med = Medication.query.get_or_404(id)
    db.session.delete(med)
    db.session.commit()
    flash('Medication deleted successfully.')
    return redirect(url_for('main.medications'))

@bp.route('/medication/<int:id>')
@login_required
def medication(id):
    med = Medication.query.get_or_404(id)
    form = LoadUnloadForm()
    return render_template('medication.html', title=med.name, medication=med, form=form)

@bp.route('/medication/<int:id>/load', methods=['POST'])
@login_required
@role_required('admin', 'pharmacist')
def load_medication(id):
    med = Medication.query.get_or_404(id)
    form = LoadUnloadForm()
    if form.validate_on_submit():
        med.quantity += form.quantity.data
        transaction = Transaction(
            user_id=current_user.id,
            medication_id=med.id,
            transaction_type='load',
            quantity=form.quantity.data
        )
        db.session.add(transaction)
        db.session.commit()
        flash(f'Loaded {form.quantity.data} units of {med.name}.')
    else:
        flash('Error loading medication.')
    return redirect(url_for('main.medication', id=id))

@bp.route('/scan')
@login_required
def scan():
    return render_template('scan.html', title='Scan QR Code')

@bp.route('/medication/<int:id>/unload', methods=['POST'])
@login_required
@role_required('admin', 'pharmacist')
def unload_medication(id):
    med = Medication.query.get_or_404(id)
    form = LoadUnloadForm()
    if form.validate_on_submit():
        if med.quantity >= form.quantity.data:
            med.quantity -= form.quantity.data
            transaction = Transaction(
                user_id=current_user.id,
                medication_id=med.id,
                transaction_type='unload',
                quantity=form.quantity.data
            )
            db.session.add(transaction)
            db.session.commit()
            flash(f'Unloaded {form.quantity.data} units of {med.name}.')
        else:
            flash('Not enough stock to unload.')
    else:
        flash('Error unloading medication.')
    return redirect(url_for('main.medication', id=id))

@bp.route('/process_qr/<string:qr_data>')
@login_required
def process_qr(qr_data):
    med = Medication.query.filter_by(aic_code=qr_data).first()
    if med:
        return redirect(url_for('main.medication', id=med.id))
    else:
        flash(f"Medication with QR code '{qr_data}' not found.")
        return redirect(url_for('main.scan'))

@bp.route('/reports', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def reports():
    form = ReportForm()
    transactions = None
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        transactions = Transaction.query.filter(
            Transaction.timestamp.between(start_date, end_date)
        ).all()
    return render_template('reports.html', title='Reports', form=form, transactions=transactions)
