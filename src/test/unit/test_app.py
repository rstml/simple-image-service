from unittest import TestCase
import app


class TestApp(TestCase):

    def test_load_from_base64(self):
        assert app._load_from_base64('b2sh').read() == b'ok!'

    ### TODO: Increase coverage