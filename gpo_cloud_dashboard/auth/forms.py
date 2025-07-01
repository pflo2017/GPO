from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from ..models import User


class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField(
        'Confirm Password', 
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    tenant_id = SelectField('Organization', validators=[DataRequired()])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Validate username is unique"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        """Validate email is unique"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class CreateTenantForm(FlaskForm):
    """Create tenant form"""
    tenant_name = StringField('Organization Name', validators=[DataRequired(), Length(min=2, max=100)])
    
    # Admin user fields (only required for first tenant)
    admin_username = StringField('Admin Username', validators=[Length(min=3, max=64)])
    admin_email = EmailField('Admin Email', validators=[Email()])
    admin_password = PasswordField('Admin Password', validators=[Length(min=8)])
    admin_password2 = PasswordField(
        'Confirm Admin Password',
        validators=[EqualTo('admin_password', message='Passwords must match')]
    )
    
    submit = SubmitField('Create Organization')
    
    def validate_admin_username(self, admin_username):
        """Validate admin username is unique"""
        if admin_username.data:
            user = User.query.filter_by(username=admin_username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
    
    def validate_admin_email(self, admin_email):
        """Validate admin email is unique"""
        if admin_email.data:
            user = User.query.filter_by(email=admin_email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.') 