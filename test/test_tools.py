from pass_secret_service.common.tools import SerialMixin


class TestTools:
    def test_serial_mixin(self):
        class A(SerialMixin):
            pass

        class B(SerialMixin):
            pass

        res = [A._serial(), A._serial(), B._serial(), A._serial(), B._serial(), B._serial()]
        expect = [1, 2, 1, 3, 2, 3]
        assert res == expect
