# STRIDE D10 - $ cap and token prices that would turn the spend stop off
# float() takes 'nan', 'inf' and 0, with any of those the cap in budget.py can never trip so get_settings has to refuse them before a run
import unittest

from helpers import quiet_settings

NORMAL_CAP = "0.50"  # cap from .env.example
PRICE_VARS = ("AS_PRICE_IN_PER_MTOK", "AS_PRICE_OUT_PER_MTOK")


class DollarAmountTests(unittest.TestCase):

    def assert_cap_refused(self, raw):
        with self.assertRaises(ValueError) as caught:
            quiet_settings(AS_MAX_USD=raw)
        self.assertEqual(str(caught.exception), f"AS_MAX_USD must be a finite number of at least 0 (got {raw!r})")

    def test_nan_cap(self):
        # 'spent > nan' is never true so the cap would never trip
        self.assert_cap_refused("nan")

    def test_inf_cap(self):
        # no spend is ever more than inf
        self.assert_cap_refused("inf")

    def test_negative_cap(self):
        self.assert_cap_refused("-1")

    def test_zero_price(self):
        # price of 0 (in or out) makes every call $0 so it never hits the cap
        for name in PRICE_VARS:
            with self.subTest(setting=name):
                with self.assertRaises(ValueError) as caught:
                    quiet_settings(**{name: "0"})
                self.assertEqual(str(caught.exception), f"{name} must be a finite number above 0 (got '0')")

    def test_normal_cap_ok(self):
        # 0.50 is fine, with the default $3 / $15 prices
        settings = quiet_settings(AS_MAX_USD=NORMAL_CAP)
        self.assertEqual(settings.max_usd, 0.5)
        self.assertEqual(settings.price_in_per_mtok, 3.0)
        self.assertEqual(settings.price_out_per_mtok, 15.0)


if __name__ == "__main__":
    unittest.main()
