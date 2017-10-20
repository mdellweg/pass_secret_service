#!/usr/bin/env python3

import unittest
from common.tools import SerialMixin


class TestTools(unittest.TestCase):

    def test_serial_mixin(self):
        class A(SerialMixin):
            pass

        class B(SerialMixin):
            pass

        res = [ A._serial(), A._serial(), B._serial(), A._serial(), B._serial(), B._serial() ]
        expect = [ 1, 2, 1, 3, 2, 3 ]
        self.assertEqual(res, expect)


if __name__ == "__main__":
    unittest.main()
