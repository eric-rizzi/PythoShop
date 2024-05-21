from unittest import mock

from PythoShop import ImageDisplay


def test_set_extra_1() -> None:
    image = ImageDisplay(is_primary=True)

    assert image.is_primary == True
    assert image.uix_image == None
    assert image.bytes == None
    assert image.is_image_loaded() == False


def test_set_extra_2() -> None:
    image = ImageDisplay(is_primary=False)
    image.load_image("fake", "data")

    assert image.is_primary == False
    assert image.uix_image == "fake"
    assert image.bytes == "data"
    assert image.is_image_loaded() == True
