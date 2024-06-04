from unittest import TestCase, main

from models import WeekdayEnum


class TestWeekday(TestCase):
    def test_weekday(self):
        a = "monday".upper()
        b = WeekdayEnum[a]
        self.assertEqual(b, WeekdayEnum.MONDAY)
        self.assertEqual(b.value, 1)


if __name__ == "__main__":
    main()
