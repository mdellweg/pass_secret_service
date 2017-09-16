#!/usr/bin/env python3

import sys
from common.tools import SerialMixin


def test_serial_mixin():
    class A(SerialMixin):
        pass

    class B(SerialMixin):
        pass

    res = [ A._serial(), A._serial(), B._serial(), A._serial(), B._serial(), B._serial() ]
    expect = [ 1, 2, 1, 3, 2, 3 ]
    if not res == expect:
        print("Error! {} != {}".format(res, expect))
        return 1


if __name__ == "__main__":
    # --- Test code ---

    result = test_serial_mixin()
    sys.exit(result)
