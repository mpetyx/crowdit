from django.test import TestCase
from models import Event
import datetime


class SimpleTest(TestCase):
    def test_database_is_empty(self):
        self.assertQuerysetEqual(Event.objects.all(), [])

    def test_is_expired_return_true_if_date_expired_less_than_now(self):
        event = Event(
            id=None,
            category='foobar?',
            expiryDate=datetime.datetime.now(),
        )
        self.assertTrue(event.isExpired())

    def test_is_expired_return_false_if_date_expired_greater_than_now(self):
        event = Event(
            id=None,
            category='foobar?',
            expiryDate=datetime.datetime.now() + datetime.timedelta(1),
        )
        self.assertFalse(event.isExpired())
