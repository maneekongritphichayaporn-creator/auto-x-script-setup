import unittest
from datetime import date

from content_cycle import CONTENT_TOPICS_BY_WEEKDAY, topic_for_date


class WeeklyTopicTests(unittest.TestCase):
    def test_each_weekday_uses_its_configured_topic(self) -> None:
        monday = date(2026, 10, 26)

        for offset, expected_topic in CONTENT_TOPICS_BY_WEEKDAY.items():
            with self.subTest(weekday=offset):
                self.assertEqual(topic_for_date(date.fromordinal(monday.toordinal() + offset)), expected_topic)

    def test_schedule_repeats_on_the_following_week(self) -> None:
        monday = date(2026, 10, 26)

        for weekday in range(7):
            with self.subTest(weekday=weekday):
                this_week = date.fromordinal(monday.toordinal() + weekday)
                next_week = date.fromordinal(this_week.toordinal() + 7)
                self.assertEqual(topic_for_date(this_week), topic_for_date(next_week))


if __name__ == "__main__":
    unittest.main()
