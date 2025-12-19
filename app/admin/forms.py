from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class AddCategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    parent_id = SelectField('Parent Category', coerce=int) # Choices populated dynamically
    submit = SubmitField('Add')

class AddTickerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    value = StringField('Value', validators=[DataRequired()])
    change = StringField('Change', validators=[DataRequired()])
    submit = SubmitField('Add')

class SiteSettingsForm(FlaskForm):
    announcement = StringField('Announcement')
    contact_info = StringField('Contact Info')
    submit = SubmitField('Save Settings')

class AdminActionForm(FlaskForm):
    # Generic form for actions like delete/block/verify to carry CSRF token
    submit = SubmitField('Confirm')
