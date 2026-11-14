import numpy as np
from PIL import Image
import fastlab


def make_test_image():
    arr = np.zeros((4, 4, 3), dtype=np.uint8)
    arr[..., 0] = 255   # R
    arr[..., 1] = 10    # G
    arr[..., 2] = 20    # B
    return Image.fromarray(arr)


def test_reorder_grb():
    out = fastlab.reorder_channels(make_test_image(), "grb")
    assert tuple(out[0, 0]) == (10, 255, 20)


def test_reorder_bgr():
    out = fastlab.reorder_channels(make_test_image(), "bgr")
    assert tuple(out[0, 0]) == (20, 10, 255)


def test_reorder_rgb_identity():
    out = fastlab.reorder_channels(make_test_image(), "rgb")
    assert tuple(out[0, 0]) == (255, 10, 20)


def test_reorder_invalid():
    try:
        fastlab.reorder_channels(make_test_image(), "rrr")
        assert False, "должно быть ValueError"
    except ValueError:
        pass


def test_reorder_wrong_length():
    try:
        fastlab.reorder_channels(make_test_image(), "rg")
        assert False, "должно быть ValueError"
    except ValueError:
        pass


def test_hist_figure_returns_png():
    buf = fastlab.color_hist_figure(np.array(make_test_image()), "test")
    assert buf.getvalue()[:8] == b"\x89PNG\r\n\x1a\n"


def test_mean_profile_figure_returns_png():
    buf = fastlab.mean_profile_figure(np.array(make_test_image()), 0, "test")
    assert buf.getvalue()[:8] == b"\x89PNG\r\n\x1a\n"
