from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateField
from wtforms.validators import DataRequired

class ReportForm(FlaskForm):
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Generate Report')

class MedicationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    min_stock_level = IntegerField('Minimum Stock Level', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LoadUnloadForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    load = SubmitField('Load Stock')
    unload = SubmitField('Unload Stock')
