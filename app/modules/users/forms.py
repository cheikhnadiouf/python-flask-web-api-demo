#!/usr/bin/python
# -*- coding: utf-8 -*-

# import dependencies
from wtforms import Form, StringField, TextAreaField, BooleanField, validators
from wtforms.fields.html5 import DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

from app.modules.assets.models import Asset
from app.modules.sections.models import Section
# from app.modules.sections.usersection_model import UserSection

class Form_Record_Add(Form):
    email = StringField('email', validators=[validators.DataRequired(),
                                             validators.Length(max=255, message='max 255 characters')])
    username = StringField('username', validators=[validators.DataRequired(),
                                             validators.Length(max=255, message='max 255 characters')])

    asset = QuerySelectField(query_factory=lambda: Asset.query.filter(Asset.is_active == True).all(), get_label="data_file_name", allow_blank=True)

    sections = QuerySelectMultipleField('Select Sections',
                             query_factory=lambda : Section.query.filter(Section.is_active == True).all(),
                             get_label=lambda s: s.title_en_US,
                             allow_blank=True)

    is_active = BooleanField('is_active')

    # created_at = DateField('created_at', format='%Y-%m-%d %H:%M:%S')
    created_at = DateField('created_at', format='%Y-%m-%d')