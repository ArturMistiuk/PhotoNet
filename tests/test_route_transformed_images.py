import asyncio
import unittest
from unittest.mock import AsyncMock
from unittest.mock import MagicMock, patch

from src.routes.transformed_images import create_new_transformed_image, \
    get_all_transformed_images_for_original_image_by_id, get_transformed_images_by_image_id, \
    get_qrcode_for_transformed_image, get_url_for_transformed_image, delete_transformed_image
from src.schemas.transformed_image_schemas import TransformedImageModel


class TransformedImagesRouterTestCase(unittest.TestCase):
    def setUp(self):
        self.router = MagicMock()
        self.mock_db = MagicMock()
        self.mock_user = MagicMock()
        self.mock_transformed_image = MagicMock()
        self.mock_transformed_image_id = 1
        self.mock_image_id = 1

    def test_create_new_transformed_image_success(self):
        # Ensure that the function returns a new transformed image
        body = TransformedImageModel()
        create_transformed_picture = AsyncMock(return_value=self.mock_transformed_image)
        with patch("src.routes.transformed_images.create_transformed_picture", create_transformed_picture):
            result = asyncio.run(create_new_transformed_image(body, self.mock_user, self.mock_image_id, self.mock_db))
        self.assertEqual(result, self.mock_transformed_image)

    def test_get_all_transformed_images_for_original_image_by_id_success(self):
        # Ensure that the function returns a list of transformed images for the given original image
        skip = 0
        limit = 10
        get_all_transformed_images = AsyncMock(return_value=[self.mock_transformed_image])
        with patch("src.routes.transformed_images.get_all_transformed_images", get_all_transformed_images):
            result = asyncio.run(
                get_all_transformed_images_for_original_image_by_id(skip, limit, self.mock_image_id, self.mock_db,
                                                                    self.mock_user))
        self.assertEqual(result, [self.mock_transformed_image])

    def test_get_transformed_images_by_image_id_success(self):
        # Ensure that the function returns a transformed image by its id
        get_transformed_img_by_id = AsyncMock(return_value=self.mock_transformed_image)
        with patch("src.routes.transformed_images.get_transformed_img_by_id", get_transformed_img_by_id):
            result = asyncio.run(
                get_transformed_images_by_image_id(self.mock_transformed_image_id, self.mock_db, self.mock_user))
        self.assertEqual(result, self.mock_transformed_image)

    def test_get_qrcode_for_transformed_image_success(self):
        # Ensure that the function triggers QR code generation by URL for the transformed image
        get_qrcode_transformed_image_by_id = AsyncMock(return_value=self.mock_transformed_image)
        with patch("src.routes.transformed_images.get_qrcode_transformed_image_by_id",
                   get_qrcode_transformed_image_by_id):
            result = asyncio.run(
                get_qrcode_for_transformed_image(self.mock_transformed_image_id, self.mock_db, self.mock_user))
        self.assertEqual(result, self.mock_transformed_image)

    def test_get_url_for_transformed_image_success(self):
        # Ensure that the function returns the URL of the transformed image
        get_url_transformed_image_by_id = AsyncMock(return_value=self.mock_transformed_image)
        with patch("src.routes.transformed_images.get_url_transformed_image_by_id", get_url_transformed_image_by_id):
            result = asyncio.run(
                get_url_for_transformed_image(self.mock_transformed_image_id, self.mock_db, self.mock_user))
        self.assertEqual(result, self.mock_transformed_image)

    def test_delete_transformed_image_success(self):
        # Ensure that the function returns None on successful deletion of the transformed image
        delete_transformed_image_by_id = AsyncMock(return_value=self.mock_transformed_image)
        with patch("src.routes.transformed_images.delete_transformed_image_by_id", delete_transformed_image_by_id):
            result = asyncio.run(delete_transformed_image(self.mock_transformed_image_id, self.mock_db, self.mock_user))
        self.assertIsNone(result)
