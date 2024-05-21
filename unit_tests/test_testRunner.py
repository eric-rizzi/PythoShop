from PIL import ImageDraw, ImageFont

from tests.testRunner import SideBySideImage, _create_failure_visual


def test_side_by_size_init_1() -> None:
    with open("images/even.bmp", "rb") as bmp_fp:
        sbs_image = SideBySideImage(bmp_fp.read(), "Test")
        assert sbs_image.tag == "Test"
        assert sbs_image.width == 200
        assert sbs_image.height == 150


def test_side_by_side_total_width_1() -> None:
    width = SideBySideImage.get_total_width(1)
    assert width == 240


def test_side_by_side_total_width_2() -> None:
    width = SideBySideImage.get_total_width(4)
    assert width == 900


def test_side_by_size_get_container_1() -> None:
    with open("images/even.bmp", "rb") as bmp_fp:
        sbs_image = SideBySideImage(bmp_fp.read(), "Test")

        container_image = SideBySideImage.get_container_image([sbs_image])
        assert container_image.width == 240
        assert container_image.height == 210


def test_side_by_size_get_container_2() -> None:
    with open("images/even.bmp", "rb") as bmp_fp:
        sbs_image = SideBySideImage(bmp_fp.read(), "Test")

        container_image = SideBySideImage.get_container_image([sbs_image, sbs_image, sbs_image])
        assert container_image.width == 680
        assert container_image.height == 210


def test_side_by_size_get_container_3() -> None:
    with open("images/even.bmp", "rb") as bmp_fp:
        sbs_image = SideBySideImage(bmp_fp.read(), "Test")

        container_image = SideBySideImage.get_container_image([sbs_image, sbs_image, sbs_image, sbs_image])
        assert container_image.width == 900
        assert container_image.height == 210


def test_side_by_side_add_title_1() -> None:
    with open("images/even.bmp", "rb") as bmp_fp:
        sbs_image = SideBySideImage(bmp_fp.read(), "Test")

        container_image = SideBySideImage.get_container_image([sbs_image, sbs_image, sbs_image, sbs_image])
        draw = ImageDraw.Draw(container_image)
        font = ImageFont.load_default(size=16)
        SideBySideImage.add_title_to_container_image(
            container_image,
            "Test",
            draw,
            font,
        )
        assert container_image.width == 900
        assert container_image.height == 210


def test_side_by_side_paste_into_image_1() -> None:
    with open("images/even.bmp", "rb") as bmp_fp:
        sbs_image = SideBySideImage(bmp_fp.read(), "Test")

        container_image = SideBySideImage.get_container_image([sbs_image, sbs_image, sbs_image, sbs_image])
        draw = ImageDraw.Draw(container_image)
        font = ImageFont.load_default(size=16)
        sbs_image.paste_into_image(container_image, draw, font, index=0)


def test_create_failure_visual_1() -> None:
    with open("images/even.bmp", "rb") as bmp_fp:
        bmp_bytes = bmp_fp.read()
        failure_image = _create_failure_visual(
            "test_failure",
            bmp_bytes,
            None,
            bmp_bytes,
            bmp_bytes,
        )

        assert failure_image.width == 680
        assert failure_image.height == 210


def test_create_failure_visual_2() -> None:
    with open("images/even.bmp", "rb") as bmp_fp:
        bmp_bytes = bmp_fp.read()
        failure_image = _create_failure_visual(
            "test_failure",
            bmp_bytes,
            bmp_bytes,
            bmp_bytes,
            bmp_bytes,
        )

        assert failure_image.width == 900
        assert failure_image.height == 210
