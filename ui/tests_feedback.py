from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .models import Produce, Image as ImageModel, Feedback
from django.contrib.auth.models import User


class FeedbackEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.produce = Produce.objects.create(name='test', category='test')
        # create a small fake image file for the Image.image_path field
        img_file = SimpleUploadedFile('test.jpg', b'fake-image-content', content_type='image/jpeg')
        self.image = ImageModel.objects.create(produce=self.produce, image_path=img_file, status='analyzed')

    def test_anonymous_feedback_creates_entry_with_session(self):
        # ensure session exists
        session = self.client.session
        session.save()
        data = {
            'image_id': self.image.id,
            'helpful': True,
            'explanation': 'looks good'
        }
        resp = self.client.post(reverse('submit_feedback'), data, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Feedback.objects.exists())
        fb = Feedback.objects.last()
        self.assertEqual(fb.image.id, self.image.id)
        self.assertIsNone(fb.user)
        self.assertIsNotNone(fb.session_key)

    def test_authenticated_feedback_links_user(self):
        user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(user)
        data = {
            'image_id': self.image.id,
            'helpful': False,
            'explanation': 'not accurate'
        }
        resp = self.client.post(reverse('submit_feedback'), data, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        fb = Feedback.objects.last()
        self.assertEqual(fb.user.username, 'tester')
        self.assertEqual(fb.helpful, False)