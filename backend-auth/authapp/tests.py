from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import serializers, status
from .serializers import ProfileSerializer, ProfileCreateSerializer
from .models import Profile
from rest_framework.test import APITestCase



class ProfileCreateSerializerTestCase(TestCase):
    def test_create_profile(self):
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        profile_data = {
            'user': user_data,
            'confirm_password': 'testpassword',
            'gender': 'M',
            'mobile_number': '1234567890',
            'birth_date': '1990-01-01',
            'profile_picture': None
        }
        serializer = ProfileCreateSerializer(data=profile_data)
        self.assertTrue(serializer.is_valid())
        profile = serializer.save()

        self.assertIsInstance(profile, Profile)
        self.assertIsInstance(profile.user, User)
        self.assertEqual(profile.user.username, 'testuser')
        self.assertEqual(profile.user.email, 'test@example.com')
        self.assertEqual(profile.gender, 'M')
        self.assertEqual(profile.mobile_number, '1234567890')
        self.assertEqual(profile.birth_date.strftime('%Y-%m-%d'), '1990-01-01')



class ProfileSerializerTestCase(TestCase):
    def test_profile_serializer(self):
        # Create a new user for testing
        user = User.objects.create_user(username='testuser1', email='test1@example.com', password='testpassword1')

        # Check if a profile already exists for the user
        profile, created = Profile.objects.get_or_create(user=user)

        # Update the profile data
        profile.gender = 'M'
        profile.mobile_number = '1234567897'
        profile.save()


        serializer = ProfileSerializer(instance=profile)
        expected_data = {
            'id': profile.id,
            'user': user.id,
            'gender': 'M',
            'mobile_number': '1234567897',
            'birth_date': None,
            'profile_picture': None
        }
        self.assertEqual(serializer.data['id'], expected_data['id'])
        self.assertEqual(serializer.data['user'], expected_data['user'])
        self.assertEqual(serializer.data['gender'], expected_data['gender'])
        self.assertEqual(serializer.data['mobile_number'], expected_data['mobile_number'])
        self.assertEqual(serializer.data['birth_date'], expected_data['birth_date'])
        self.assertEqual(serializer.data['profile_picture'], expected_data['profile_picture'])

class ProfileUpdateViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_profile_update(self):
        data = {
            'user': {
                'username': 'newusername',
                'email': 'newemail@example.com'
            },
            'profile': {
                'gender': 'M',
                'mobile_number': '1234567890'
            }
        }
        response = self.client.patch('/api/profile/update/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'newusername')
        self.assertEqual(response.data['user']['email'], 'newemail@example.com')
        self.assertEqual(response.data['profile']['gender'], 'M')
        self.assertEqual(response.data['profile']['mobile_number'], '1234567890')

class PasswordUpdateViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_password_update(self):
        data = {
            'old_password': 'testpassword',
            'new_password': 'newpassword',
        }
        response = self.client.post('/api/profile/password/update/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password updated successfully.')


class HomeViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_home_view_authenticated(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'Welcome to the JWT Authentication page using React Js and Django!'})

    def test_home_view_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)