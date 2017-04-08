#!/usr/bin/python
# -*- coding: utf-8 -*-

# ------- IMPORT DEPENDENCIES ------- 
import datetime
from sqlalchemy import desc
from sqlalchemy import or_

# ------- IMPORT LOCAL DEPENDENCIES  -------
from app import db

import time
from app.helpers import *
from app.modules.localization.controllers import get_locale, get_timezone

# from app.modules.sections.usersection_model import UserSection
# from app.modules.users.models import User


class UserSection(db.Model):
    __tablename__ = "usersection"
    #__table_args__ = db.PrimaryKeyConstraint('user_id', 'section_id')

    user_id = db.Column(db.Integer,db.ForeignKey('User.id'), primary_key=True)
    section_id = db.Column(db.Integer,db.ForeignKey('Section.id'), primary_key=True)



    # bidirectional attribute/collection of "user"/"usersections" and "section"/"usersections". Return object
    user = db.relationship("User", back_populates = "usersections")
    section = db.relationship("Section", back_populates ="usersections")

    # so you can do :
    # usersection1.append(User(username = 'test')))
    # or usersection1.append(user1)
    # or UserSection(user1, Section(title_en_US = 'test'), description_en_US="test")

    # Extra data
    description_en_US = db.Column(db.Text(),  index=True)
    description_fr_FR = db.Column(db.Text(),  index=True)


    updated_at = db.Column(db.Integer, default=string_datetime_utc_to_string_timestamp_utc(datetime.utcnow()), onupdate=string_datetime_utc_to_string_timestamp_utc(datetime.utcnow()))

    created_at = db.Column(db.Integer, default=string_datetime_utc_to_string_timestamp_utc(datetime.utcnow()))
    # updated_at = db.Column(db.Integer, default=time.mktime(datetime.utcnow().timetuple()), onupdate=time.mktime(datetime.utcnow().timetuple())) 
    # created_at = db.Column(db.Integer, default=time.mktime(datetime.utcnow().timetuple())) 


    def __repr__(self):
        # return '<UserSection: {}>'.format(self.id)
        return '<UserSection %r - %r >' % (self.user_id, self.section_id)





class Section(db.Model):
    __tablename__ = "Section"
    id = db.Column(db.Integer, primary_key=True)

    slug = db.Column(db.String(255), index=True, unique=True)

    title_en_US = db.Column(db.String(255),  index=True, unique=True)
    title_fr_FR = db.Column(db.String(255),  index=True, unique=True)

    description_en_US = db.Column(db.Text(),  index=True)
    description_fr_FR = db.Column(db.Text(),  index=True)

    # MANY-TO-MANY relationship with with EXTRA_DATA association and the User model
    # the cascade will delete orphaned usersections
    usersections = db.relationship('UserSection', back_populates='section', lazy='dynamic', cascade="all, delete-orphan")
    # or Get all users in view only mode 
    users = db.relationship('User', secondary='usersection', viewonly=True, back_populates='sections', lazy='dynamic')
    """
    Return UserSection objects collection 
    and requires that child objects are associated with an association instance before being appended to the parent; 
    similarly, access from parent to child goes through the association object:
    so to append sections via association
        user1.usersections.append(UserSection(section = Section(title_en_US = 'test')))
        
    or 
        UserSection(user = user1, Section(title_en_US = 'test'), extra_data="test")
    To iterate through sections objects via association, including association attributes
        for usersection in user.usersections:
            print(usersection.extra_data)
            print(usersection.section)
    WARNING : So don't use  directly user.sections.append(Section(title_en_US = 'test'))
                cause it's redundant, it will cause a duplicate INSERT on Association with 
                user.usersections.append(UserSection(section=section1))
                add  viewonly=True on secondary relationship to stop edit, create or delete operations  here
    """

    # is_active usually returns True. 
    # This should return False only in cases where we have disabled section. 
    is_active = db.Column(db.Boolean, index=True, default=True)

    updated_at = db.Column(db.Integer, default=string_datetime_utc_to_string_timestamp_utc(datetime.utcnow()), onupdate=string_datetime_utc_to_string_timestamp_utc(datetime.utcnow()))

    created_at = db.Column(db.Integer, default=string_datetime_utc_to_string_timestamp_utc(datetime.utcnow()))
    # updated_at = db.Column(db.Integer, default=time.mktime(datetime.utcnow().timetuple()), onupdate=time.mktime(datetime.utcnow().timetuple())) 
    # created_at = db.Column(db.Integer, default=time.mktime(datetime.utcnow().timetuple())) 


    def all_data(self, page, LISTINGS_PER_PAGE):
        return Section.query.order_by(desc(Section.created_at)).paginate(page, LISTINGS_PER_PAGE, False)

    def read_data(self, some_id):
        section = Section.query.filter(Section.id == some_id).first_or_404()
        return section


    def create_data(self, form):
        # dateTime conversion to timestamp
        timestamp_created_at = string_datetime_utc_to_string_timestamp_utc(form['created_at'])

        section = Section(
                                slug=form['slug'],

                                title_en_US=form['title_en_US'],
                                title_fr_FR=form['title_fr_FR'],

                                description_en_US=form['description_en_US'],
                                description_fr_FR=form['description_fr_FR'],

                                is_active = form['is_active'],
                                # convert string to integer format
                                created_at = int(timestamp_created_at)
                            )

        # MANY-TO-MANY Relationship
        for user in form['users']:
            usersection = UserSection(user = user, section = section)
            section.usersections.append(usersection)

        db.session.add(section)
        db.session.commit()

    def update_data(self, some_id, form ):
        section = Section.query.get_or_404(some_id)

        section.slug = form['slug']

        section.title_en_US = form['title_en_US']
        section.title_fr_FR = form['title_fr_FR']

        section.description_en_US = form['description_en_US']
        section.description_fr_FR = form['description_fr_FR']

        section.is_active = form['is_active']

        # dateTime conversion to timestamp
        timestamp_created_at = string_datetime_utc_to_string_timestamp_utc(form['created_at'])
        # convert string to integer format
        section.created_at = int(timestamp_created_at)

        # MANY-TO-MANY Relationship 
        section.usersections = []
        for user in form['users']:
            usersection = UserSection(user = user, section = section)
            section.usersections.append(usersection)


        db.session.commit()

    def destroy_data(self, some_id ):
        section = Section.query.get_or_404(some_id)
        db.session.delete(section)
        db.session.commit()


    def __repr__(self):
        # return '<Section: {}>'.format(self.id)
        return '<Section %r>' % self.id


