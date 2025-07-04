from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length
from wtforms.fields import DateField

class LinguistUploadForm(FlaskForm):
    """Form for uploading linguist profiles via CSV/Excel file"""
    file = FileField('Linguist File', validators=[
        FileRequired(),
        FileAllowed(['csv', 'xlsx', 'xls'], 'Only CSV and Excel files are allowed!')
    ])
    submit = SubmitField('Upload Linguists')

class LinguistProfileForm(FlaskForm):
    """Form for manually creating/editing linguist profiles"""
    internal_id = StringField('Internal ID', validators=[DataRequired(), Length(max=100)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=200)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=200)])
    specializations = TextAreaField('Specializations (comma-separated)')
    source_languages = StringField('Source Languages (comma-separated)', validators=[DataRequired()])
    target_languages = StringField('Target Languages (comma-separated)', validators=[DataRequired()])
    quality_rating = SelectField('Quality Rating', choices=[
        ('', 'Select Rating'),
        ('Certified', 'Certified'),
        ('Preferred', 'Preferred'),
        ('Standard', 'Standard'),
        ('Native Speaker', 'Native Speaker')
    ])
    general_capacity_words_per_day = IntegerField('Daily Capacity (words)')
    status = SelectField('Status', choices=[
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('On Leave', 'On Leave')
    ], default='Active')
    submit = SubmitField('Save Linguist')

class NewProjectRequestForm(FlaskForm):
    """Form for initiating a new project analysis request"""
    project_name = StringField('Project Name', validators=[DataRequired(), Length(max=255)])
    client_name = StringField('Client Name', validators=[DataRequired(), Length(max=255)])
    source_lang = StringField('Source Language', validators=[DataRequired(), Length(max=50)])
    target_lang = StringField('Target Language', validators=[DataRequired(), Length(max=50)])
    desired_deadline = DateField('Desired Deadline', validators=[DataRequired()])
    content_type_selection = SelectField('Content Type', choices=[
        ('Legal', 'Legal'),
        ('Medical', 'Medical'),
        ('Marketing', 'Marketing'),
        ('General', 'General'),
        ('Technical', 'Technical'),
        ('Financial', 'Financial'),
        ('IT', 'IT')
    ], validators=[DataRequired()])
    selected_linguist_id_for_planning = SelectField('Preferred Linguist (Optional)', coerce=str, validators=[Optional()])
    submit = SubmitField('Initiate Project Analysis') 