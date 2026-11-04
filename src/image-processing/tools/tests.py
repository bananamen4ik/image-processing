"""Application tests."""

import io
from pathlib import Path

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import (
    TestCase,
    override_settings,
)
from django.urls import reverse_lazy
from faker import Faker
from PIL import Image

from custom_auth.models import CustomUser
from tools.forms import (
    ConvertForm,
    ResizeForm,
)
from tools.models import Operation
from tools.tasks import (
    image_convert_processing,
    image_resize_processing,
)


class IndexViewTests(TestCase):
    """Tests the index view."""

    URI = reverse_lazy('tools:index')
    fake = Faker()

    def setUp(self) -> None:
        """Sets up the user."""
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )

    def test_accessibility(self) -> None:
        """Checking that the page is accessible."""
        response = self.client.get(self.URI)
        self.assertRedirects(
            response,
            f'{settings.LOGIN_URL}?{REDIRECT_FIELD_NAME}={self.URI}',
        )

        self.client.force_login(self.user)

        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 200)


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class ResizeViewTests(TestCase):
    """Tests the resize view."""

    URI = reverse_lazy('tools:resize')
    fake = Faker()
    DEFAULT_IMAGE_NAME = 'test.png'

    def setUp(self) -> None:
        """Sets up the user."""
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )
        self.files_path: list[str] = []

    def tearDown(self) -> None:
        """Deletes stored files."""
        for file_path in self.files_path:
            Path(file_path).unlink(missing_ok=True)

    def test_accessibility(self) -> None:
        """Checking that the page is accessible."""
        response = self.client.get(self.URI)
        self.assertRedirects(
            response,
            f'{settings.LOGIN_URL}?{REDIRECT_FIELD_NAME}={self.URI}',
        )

        self.client.force_login(self.user)

        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 200)

    def test_invalid_image_format(self) -> None:
        """Tests that the invalid image format is rejected."""
        self.client.force_login(self.user)
        image = get_image_file('test.jpg')

        response = self.client.post(
            self.URI,
            data={
                'uploaded_image': image,
                'width': 100,
                'height': 100,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'uploaded_image',
            str(
                ResizeForm.error_messages['invalid_image_format']
                % {
                    'real_format': 'PNG',
                }
            ),
        )

    def test_invalid_max_pixels(self) -> None:
        """Checks the processing of overflow pixels."""
        self.client.force_login(self.user)

        image = get_image_file(self.DEFAULT_IMAGE_NAME)
        pixel_value = 10_000

        response = self.client.post(
            self.URI,
            data={
                'uploaded_image': image,
                'width': pixel_value,
                'height': pixel_value,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            None,
            str(
                ResizeForm.error_messages['invalid_max_pixels']
                % {
                    'current_pixels': pixel_value * pixel_value,
                    'max_pixels': ResizeForm.MAX_PIXELS,
                }
            ),
        )

    def test_required_width_and_height(self) -> None:
        """Checks whether the 'width' and 'height' fields is required."""
        self.client.force_login(self.user)

        image = get_image_file(self.DEFAULT_IMAGE_NAME)

        response = self.client.post(
            self.URI,
            data={
                'uploaded_image': image,
            },
        )

        self.assertFormError(
            response.context['form'],
            'width',
            str(ResizeForm.base_fields['width'].error_messages['required']),
        )

        self.assertFormError(
            response.context['form'],
            'height',
            str(ResizeForm.base_fields['height'].error_messages['required']),
        )

    def test_valid_data(self) -> None:
        """Tests the functionality using valid data."""
        self.client.force_login(self.user)

        image = get_image_file(self.DEFAULT_IMAGE_NAME)

        response = self.client.post(
            self.URI,
            data={
                'uploaded_image': image,
                'width': 200,
                'height': 200,
            },
        )

        self.assertRedirects(
            response,
            str(self.URI),
        )

        operation: Operation | None = Operation.objects.first()
        assert operation is not None

        self.files_path.append(operation.uploaded_image.path)

        self.assertIsNotNone(operation.processed_image)
        self.files_path.append(operation.processed_image.path)

        self.assertEqual(operation.status, Operation.Status.COMPLETED)
        self.assertIsNotNone(operation.processed_at)
        self.assertTrue(Path(operation.uploaded_image.path).is_file())
        self.assertTrue(Path(operation.processed_image.path).is_file())


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class ConvertViewTests(TestCase):
    """Tests the convert view."""

    URI = reverse_lazy('tools:convert')
    fake = Faker()
    DEFAULT_IMAGE_NAME = 'test.png'

    def setUp(self) -> None:
        """Sets up the user."""
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )
        self.files_path: list[str] = []

    def tearDown(self) -> None:
        """Deletes stored files."""
        for file_path in self.files_path:
            Path(file_path).unlink(missing_ok=True)

    def test_accessibility(self) -> None:
        """Checking that the page is accessible."""
        response = self.client.get(self.URI)
        self.assertRedirects(
            response,
            f'{settings.LOGIN_URL}?{REDIRECT_FIELD_NAME}={self.URI}',
        )

        self.client.force_login(self.user)

        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 200)

    def test_invalid_image_format(self) -> None:
        """Tests that the invalid image format is rejected."""
        self.client.force_login(self.user)
        image = get_image_file('test.jpg')

        response = self.client.post(
            self.URI,
            data={
                'uploaded_image': image,
                'extension': '.png',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'uploaded_image',
            str(
                ConvertForm.error_messages['invalid_image_format']
                % {
                    'real_format': 'PNG',
                },
            ),
        )

    def test_valid_data(self) -> None:
        """Tests the functionality using valid data."""
        self.client.force_login(self.user)

        image = get_image_file(self.DEFAULT_IMAGE_NAME)

        response = self.client.post(
            self.URI,
            data={
                'uploaded_image': image,
                'extension': '.jpg',
            },
        )

        self.assertRedirects(response, str(self.URI))

        operation: Operation | None = Operation.objects.first()
        assert operation is not None

        self.files_path.append(operation.uploaded_image.path)

        self.assertIsNotNone(operation.processed_image)
        self.files_path.append(operation.processed_image.path)

        self.assertEqual(operation.status, Operation.Status.COMPLETED)
        self.assertIsNotNone(operation.processed_at)
        self.assertTrue(Path(operation.uploaded_image.path).is_file())
        self.assertTrue(Path(operation.processed_image.path).is_file())

    def test_invalid_extension(self) -> None:
        """Tests that the invalid extension is rejected."""
        self.client.force_login(self.user)

        image = get_image_file(self.DEFAULT_IMAGE_NAME)
        extension = 'invalid-extension'

        response = self.client.post(
            self.URI,
            data={
                'uploaded_image': image,
                'extension': extension,
            },
        )

        self.assertFormError(
            response.context['form'],
            'extension',
            str(
                ConvertForm.base_fields['extension'].error_messages['invalid_choice']
                % {
                    'value': extension,
                },
            ),
        )


class ResizeTaskTests(TestCase):
    """Tests the resize task."""

    fake = Faker()
    DEFAULT_IMAGE_NAME = 'test.png'

    def setUp(self) -> None:
        """Sets up the data."""
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )
        self.operation = Operation.objects.create(
            user=self.user,
            uploaded_image=get_image_file(self.DEFAULT_IMAGE_NAME),
            parameters={
                'width': 100,
                'height': 100,
            },
            type=Operation.Type.RESIZE,
        )
        self.files_path: list[str] = []
        self.files_path.append(self.operation.uploaded_image.path)

    def tearDown(self) -> None:
        """Deletes stored files."""
        for file_path in self.files_path:
            Path(file_path).unlink(missing_ok=True)

    def test_valid_data(self) -> None:
        """Tests the functionality using valid data."""
        image_resize_processing(self.operation.id)
        self.operation.refresh_from_db()

        self.assertIsNotNone(self.operation.processed_image)
        self.files_path.append(self.operation.processed_image.path)

        self.assertEqual(self.operation.status, Operation.Status.COMPLETED)
        self.assertIsNotNone(self.operation.processed_at)
        self.assertTrue(Path(self.operation.processed_image.path).is_file())

    def test_invalid_status(self) -> None:
        """Checks for operations with an invalid status."""
        self.operation.status = Operation.Status.COMPLETED
        self.operation.save(update_fields=['status'])

        with self.assertRaises(ValueError):
            image_resize_processing(self.operation.id)

    def test_invalid_type(self) -> None:
        """Checks for operations with an invalid type."""
        self.operation.type = Operation.Type.CONVERT
        self.operation.save(update_fields=['type'])

        with self.assertRaises(ValueError):
            image_resize_processing(self.operation.id)

    def test_removed_uploaded_image(self) -> None:
        """Tests the functionality using a removed uploaded file."""
        Path(self.operation.uploaded_image.path).unlink()

        with self.assertRaises(FileNotFoundError):
            image_resize_processing(self.operation.id)


class ConvertTaskTests(TestCase):
    """Tests the convert task."""

    fake = Faker()
    DEFAULT_IMAGE_NAME = 'test.png'

    def setUp(self) -> None:
        """Sets up the data."""
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )
        self.operation = Operation.objects.create(
            user=self.user,
            uploaded_image=get_image_file(self.DEFAULT_IMAGE_NAME),
            parameters={
                'extension': '.jpg',
                'format': 'JPEG',
            },
            type=Operation.Type.CONVERT,
        )
        self.files_path: list[str] = []
        self.files_path.append(self.operation.uploaded_image.path)

    def tearDown(self) -> None:
        """Deletes stored files."""
        for file_path in self.files_path:
            Path(file_path).unlink(missing_ok=True)

    def test_valid_data(self) -> None:
        """Tests the functionality using valid data."""
        image_convert_processing(self.operation.id)
        self.operation.refresh_from_db()

        self.assertIsNotNone(self.operation.processed_image)
        self.files_path.append(self.operation.processed_image.path)

        self.assertEqual(self.operation.status, Operation.Status.COMPLETED)
        self.assertIsNotNone(self.operation.processed_at)
        self.assertTrue(Path(self.operation.processed_image.path).is_file())

    def test_invalid_status(self) -> None:
        """Checks for operations with an invalid status."""
        self.operation.status = Operation.Status.COMPLETED
        self.operation.save(update_fields=['status'])

        with self.assertRaises(ValueError):
            image_convert_processing(self.operation.id)

    def test_invalid_type(self) -> None:
        """Checks for operations with an invalid type."""
        self.operation.type = Operation.Type.RESIZE
        self.operation.save(update_fields=['type'])

        with self.assertRaises(ValueError):
            image_convert_processing(self.operation.id)

    def test_removed_uploaded_image(self) -> None:
        """Tests the functionality using a removed uploaded file."""
        Path(self.operation.uploaded_image.path).unlink()

        with self.assertRaises(FileNotFoundError):
            image_convert_processing(self.operation.id)


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
