from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField, TextAreaField, FileField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from flask_wtf.file import FileField, FileAllowed

class SignupForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_email(self, email):
        from .model import User
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("Email already registered.")
        
    def validate_username(self, username):
        from .model import User
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username already taken.")
        
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")
    
class PhotoUploadForm(FlaskForm):
    photo = FileField("Profile Picture", validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField("Upload")
    
class ReportForm(FlaskForm):
    reason = TextAreaField("Reason", validators=[DataRequired()])
    submit = SubmitField("Report User")
    
class PasswordResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Reset Password")
    
class ClientForm(FlaskForm):
    client_name = StringField("Client Name", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Save Client")
    
class HairProfileForm(FlaskForm):
    natural_colour = SelectField(
        "Natural Colour",
        choices=[
            ("black", "Black"),
            ("brown", "Brown"),
            ("blonde", "Blonde"),
            ("red", "Red")
        ],
        validators=[Optional()]
    )

    current_colour = StringField("Current Colour", validators=[Optional(), Length(max=50)])

    texture = SelectField(
        "Texture",
        choices=[
            ("straight", "Straight"),
            ("wavy", "Wavy"),
            ("curly", "Curly"),
            ("coily", "Coily")
        ],
        validators=[Optional()]
    )

    porosity = SelectField(
        "Porosity",
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High")
        ],
        validators=[Optional()]
    )

    chem_history = TextAreaField("Chemical History", validators=[Optional()])
    
    hair_image = FileField(
        "Upload Hair Image",
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
        ]
    )

    submit = SubmitField("Save Hair Profile")