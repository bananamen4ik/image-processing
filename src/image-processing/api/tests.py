"""Application Tests."""

import io
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse_lazy
from faker import Faker
from PIL import Image
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from api.serializers import ProfileRemainingOperationsResponseSerializer
from custom_auth.models import CustomUser
from tools.models import Operation


class TokenCreatePostSaveTests(TestCase):
    """Tests the creation of a token for the user after a signal."""

    fake = Faker()

    def setUp(self) -> None:
        """Creates a user."""
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )

    def test_create_token(self) -> None:
        """Tests token creation."""
        token = Token.objects.get(user=self.user)

        self.assertEqual(token.user, self.user)


class ProfileRemainingOperationsViewTests(APITestCase):
    """Tests the profile remaining operations view."""

    fake = Faker()
    URI = reverse_lazy('api:profile_remaining_operations')

    def setUp(self) -> None:
        """Creates a user."""
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )

    def test_get(self) -> None:
        """Tests get view method."""
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)

        serializer = ProfileRemainingOperationsResponseSerializer(
            instance={
                'remaining_operations': self.user.user_profile.daily_operation_limit,
            },
        )
        response = self.client.get(self.URI)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class ResizeOperationViewTests(APITestCase):
    """Tests the resize operation view."""

    fake = Faker()
    URI = reverse_lazy('api:tools_resize')

    def setUp(self) -> None:
        """Creates a user."""
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )
        self.files_path: list[str] = []

    def tearDown(self) -> None:
        """Deletes stored files."""
        for file_path in self.files_path:
            Path(file_path).unlink()

    def test_get(self) -> None:
        """Tests get view method."""
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)

        operation = create_operation(
            user=self.user,
            image_name='test.png',
            parameters={
                'width': 100,
                'height': 100,
            },
            operation_type=Operation.Type.RESIZE,
        )

        self.files_path.append(operation.uploaded_image.path)

        response = self.client.get(self.URI)
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('next', data)
        self.assertIn('previous', data)
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)

    def test_post_valid_data(self) -> None:
        """Tests post method with valid data."""
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)

        response = self.client.post(
            self.URI,
            data={
                'uploaded_image': get_image_file('test.png'),
                'width': 10,
                'height': 10,
            },
            format='multipart',
        )
        operation = Operation.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(operation)
        assert operation is not None
        self.files_path.append(operation.uploaded_image.path)

    def test_post_invalid_data(self) -> None:
        """Tests post method with invalid data."""
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)

        response = self.client.post(
            self.URI,
            data={
                'uploaded_image': get_image_file('test.png'),
                'width': 10,
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ConvertOperationViewTests(APITestCase):
    """Tests the convert operation view."""

    fake = Faker()
    URI = reverse_lazy('api:tools_convert')

    def setUp(self) -> None:
        """Creates a user."""
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )
        self.files_path: list[str] = []

    def tearDown(self) -> None:
        """Deletes stored files."""
        for file_path in self.files_path:
            Path(file_path).unlink()

    def test_get(self) -> None:
        """Tests get view method."""
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)

        operation = create_operation(
            user=self.user,
            image_name='test.png',
            parameters={
                'extension': '.gif',
            },
            operation_type=Operation.Type.CONVERT,
        )

        self.files_path.append(operation.uploaded_image.path)

        response = self.client.get(self.URI)
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('next', data)
        self.assertIn('previous', data)
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)

    def test_post_valid_data(self) -> None:
        """Tests post method with valid data."""
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)

        response = self.client.post(
            self.URI,
            data={
                'uploaded_image': get_image_file('test.png'),
                'extension': '.gif',
            },
            format='multipart',
        )
        operation = Operation.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(operation)
        assert operation is not None

        self.files_path.append(operation.uploaded_image.path)

    def test_post_invalid_data(self) -> None:
        """Tests post method with invalid data."""
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)

        response = self.client.post(
            self.URI,
            data={
                'uploaded_image': get_image_file('test.png'),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OptimizeOperationViewTests(APITestCase):
    """Tests the optimize operation view."""

    fake = Faker()
    URI = reverse_lazy('api:tools_optimize')

    def setUp(self) -> None:
        """Creates a user."""
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )
        self.files_path: list[str] = []

    def tearDown(self) -> None:
        """Deletes stored files."""
        for file_path in self.files_path:
            Path(file_path).unlink()

    def test_get(self) -> None:
        """Tests get view method."""
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)

        operation = create_operation(
            user=self.user,
            image_name='test.png',
            parameters={},
            operation_type=Operation.Type.OPTIMIZE,
        )

        self.files_path.append(operation.uploaded_image.path)

        response = self.client.get(self.URI)
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('next', data)
        self.assertIn('previous', data)
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)

    def test_post_valid_data(self) -> None:
        """Tests post method with valid data."""
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)

        response = self.client.post(
            self.URI,
            data={
                'uploaded_image': get_image_file('test.png'),
            },
            format='multipart',
        )
        operation = Operation.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(operation)
        assert operation is not None

        self.files_path.append(operation.uploaded_image.path)

    def test_post_invalid_data(self) -> None:
        """Tests post method with invalid data."""
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)

        response = self.client.post(
            self.URI,
            data={},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


def create_operation(
    user: CustomUser,
    image_name: str,
    parameters: dict,
    operation_type: Operation.Type,
) -> Operation:
    """Creates an operation with the status CREATED."""
    return Operation.objects.create(
        user=user,
        uploaded_image=get_image_file(image_name),
        parameters=parameters,
        type=operation_type,
    )


def get_image_file(
    name: str,
    size: tuple[int, int] = (100, 100),
    color: str = 'green',
    pil_format: str = 'PNG',
    content_type: str = 'image/png',
) -> SimpleUploadedFile:
    """Creates an image file in memory."""
    image = Image.new('RGB', size, color)
    buffer = io.BytesIO()
    image.save(buffer, format=pil_format)

    return SimpleUploadedFile(
        name,
        buffer.getvalue(),
        content_type,
    )
