import unittest
from django.test import TestCase
from crowdit.models import *


class TestPerson(TestCase):
    def test_get_image_return_proper_string_when_photo_is_set(self):
        person = Person.objects.create()
        person.photo = 'foobar'
        self.assertTrue("<img src='https://crowdit-media.s3.amazonaws.com/foobar" in person.get_image())
        self.assertTrue("&AWSAccessKeyId=AKIAIB6Q2NFEOHYHIE4Q' width=97 height=72/>" in person.get_image())

    def test_get_image_return_empty_string_when_photo_is_not_set(self):
        person = Person.objects.create()
        person.photo = ''
        self.assertEquals('', person.get_image())


class TestCelebrity(TestCase):
    def test_get_image_return_proper_string_when_photo_is_set(self):
        celebrity = Celebrity.objects.create()
        celebrity.photo = 'foobar'
        self.assertTrue("<img src='https://crowdit-media.s3.amazonaws.com/foobar" in celebrity.get_image())
        self.assertTrue("&AWSAccessKeyId=AKIAIB6Q2NFEOHYHIE4Q' width=97 height=72/>" in celebrity.get_image())

    def test_get_image_return_empty_string_when_photo_is_not_set(self):
        celebrity = Celebrity.objects.create()
        celebrity.photo = ''
        self.assertEquals('', celebrity.get_image())


class TestAward(TestCase):
    def test_get_image_return_proper_string_when_photo_is_set(self):
        celebrity = Celebrity.objects.create()
        event = Event.objects.create(userCreated=celebrity, activationDate='2012-09-01T13:20:30+03:00',
            openingDate='2012-10-20T13:20:30+03:00', expiryDate='2012-10-21T13:20:30+03:00')
        award = Award.objects.create(event=event, points=100, numberLeft=10)
        award.image = 'foobar'
        self.assertTrue("<img src='https://crowdit-media.s3.amazonaws.com/foobar" in award.get_image())
        self.assertTrue("&AWSAccessKeyId=AKIAIB6Q2NFEOHYHIE4Q' width=97 height=72/>" in award.get_image())

    def test_get_image_return_empty_string_when_photo_is_not_set(self):
        celebrity = Celebrity.objects.create()
        event = Event.objects.create(userCreated=celebrity, activationDate='2012-09-01T13:20:30+03:00',
            openingDate='2012-10-20T13:20:30+03:00', expiryDate='2012-10-21T13:20:30+03:00')
        award = Award.objects.create(event=event, points=100, numberLeft=10)
        award.image = ''
        self.assertTrue("" in award.get_image())


class TestEvent(TestCase):
    def test_get_image_return_proper_string_when_photo_is_set(self):
        event = Event.objects.create(activationDate='2012-09-01T13:20:30+03:00',
            openingDate='2012-10-20T13:20:30+03:00', expiryDate='2012-10-21T13:20:30+03:00')
        event.image = 'foobar'
        self.assertTrue("<img src='https://crowdit-media.s3.amazonaws.com/foobar" in event.get_image())
        self.assertTrue("&AWSAccessKeyId=AKIAIB6Q2NFEOHYHIE4Q' width=97 height=72/>" in event.get_image())

    def test_get_image_return_empty_string_when_photo_is_not_set(self):
        event = Event.objects.create(activationDate='2012-09-01T13:20:30+03:00',
            openingDate='2012-10-20T13:20:30+03:00', expiryDate='2012-10-21T13:20:30+03:00')
        event.image = ''
        self.assertEquals('', event.get_image())


class TestCreateUserProfile(unittest.TestCase):
    def test_create_user_profile_return_null_when_not_created(self):
        self.assertFalse(create_user_profile('bar', 'foo', False))


class TestEventPersonManager(unittest.TestCase):
    def test_is_person_attending_event_return_true_when_person_and_event_found_on_event_person_table(self):
        person = Person.objects.create(username='foo')
        celebrity = Celebrity.objects.create(username='bar')
        event = Event.objects.create(userCreated=celebrity, activationDate='2012-09-01T13:20:30+03:00',
            openingDate='2012-10-20T13:20:30+03:00', expiryDate='2012-10-21T13:20:30+03:00')
        EventPerson.objects.create(event=event, person=person)
        self.assertTrue(EventPerson.objects.is_person_attending_event(person, event))

    def test_is_person_attending_event_return_false_when_person_or_event_not_found_on_event_person_table(self):
        person_attending = Person.objects.create(username='foo2')
        person_not_attending = Person.objects.create(username='foobar2')
        celebrity = Celebrity.objects.create(username='bar2')
        event_attended = Event.objects.create(userCreated=celebrity, activationDate='2012-09-01T13:20:30+03:00',
            openingDate='2012-10-20T13:20:30+03:00', expiryDate='2012-10-21T13:20:30+03:00')
        event_not_attended = Event.objects.create(userCreated=celebrity, activationDate='2012-09-01T13:20:30+03:00',
            openingDate='2012-10-20T13:20:30+03:00', expiryDate='2012-10-21T13:20:30+03:00')
        EventPerson.objects.create(event=event_attended, person=person_attending)
        self.assertFalse(EventPerson.objects.is_person_attending_event(person_not_attending, event_attended))
        self.assertFalse(EventPerson.objects.is_person_attending_event(person_attending, event_not_attended))
