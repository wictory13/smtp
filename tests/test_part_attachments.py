import os
import unittest
from base64 import b64encode
from sender import Sender
from filecmp import cmp
from contextlib import suppress

FIXED_SIZE = 8 * 1024 * 1024


class TestPartAttachments(unittest.TestCase):
    def setUp(self):
        self.files = set()

    def test_part_attachments_divided_by_fixed_size(self):
        file_name = 'test_file.txt'
        self.files.add(file_name)
        merged_name = 'merged_file.txt'
        self.files.add(merged_name)
        with open(file_name, 'w') as f:
            f.seek(16 * 1024 * 1024 - 2)
            f.write('/0')
        parts = Sender.cut_attachment(file_name, file_name)
        with open(merged_name, 'w') as f:
            for name, _ in parts:
                self.files.add(name)
                with open(name) as f2:
                    f.write(f2.read())
        self.assertEqual(2, len(parts))
        self.assertTrue(cmp(file_name, merged_name))
        for part in parts:
            self.assertEqual(os.path.getsize(part[0]), FIXED_SIZE)

    def test_part_attachments_zero_size(self):
        file_name = 'test_file.txt'
        self.files.add(file_name)
        data = b64encode(os.urandom(0)).decode()
        with open(file_name, 'w') as f:
            f.write(data)
        parts = Sender.cut_attachment(file_name, file_name)
        self.assertFalse(parts)

    def test_part_attachments_not_divided_by_fixed_size(self):
        file_name = 'test_file.txt'
        self.files.add(file_name)
        merged_name = 'merged_file.txt'
        self.files.add(merged_name)
        data = b64encode(os.urandom(25 * 1024 * 1024)).decode()
        with open(file_name, 'w') as f:
            f.write(data)
        parts = Sender.cut_attachment(file_name, file_name)
        with open(merged_name, 'w') as f:
            for name, _ in parts:
                self.files.add(name)
                with open(name) as f2:
                    f.write(f2.read())
        self.assertEqual(5, len(parts))
        self.assertTrue(cmp(file_name, merged_name))
        for part in parts:
            self.assertLessEqual(os.path.getsize(part[0]), FIXED_SIZE)

    def tearDown(self):
        for filename in self.files:
            with suppress(OSError):
                os.remove(filename)
