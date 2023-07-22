import unittest

from main import create_digest


class MyTestCase(unittest.TestCase):
    def test_digest(self):
        digest = create_digest(1)
        print(digest)

        self.assertEqual(True, digest)  # add assertion here


if __name__ == '__main__':
    unittest.main()
