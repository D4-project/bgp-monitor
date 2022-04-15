import unittest
from unittest import suite
import BGPFilter


class BGPFilterTestMethods(unittest.TestCase):
    def setUp(self):
        self.__filter = BGPFilter.BGPFilter()

    def tearDown(self):
        pass

    def test_IntervalNotSet(self):
        with self.assertRaises(ValueError):
            self.__filter.set_record_mode(True, "2022-01-01 10:10:00", None)

    def test_InvalidDateFormat(self):
        with self.assertRaises(ValueError):
            self.__filter.set_record_mode(True, "dergeg", "2022-1-15 10:110:00")

    def test_invalidDateInterval(self):
        with self.assertRaises(ValueError):
            self.__filter.set_record_mode(True, "2022-01-01 10:10:00", "2022-01-01 10:00:00")

    def test_asn_match_type(self):
        with self.assertRaises(ValueError):
            self.__filter.set_cidr_filter(True, "azd", ["14555", "azza"])

    def test_asn_asn_list(self):
        with self.assertRaises(Exception):
            self.__filter.set_cidr_filter(True, "exact", ["14555", "azza"])


if __name__ == "__main__":
    unittest.main()

    """
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(BGPFilterTestMethods('test_IntervalNotSet'))
    suite.addTest(BGPFilterTestMethods('test_InvalidDateFormat'))
    suite.addTest(BGPFilterTestMethods('test_invalidDateInterval'))
    return suite

    filter.json_out = args.json_output_file
    filter.countries_filter = args.country_filter
    filter.asn_filter = args.asn_filter
    filter.set_cidr_filter(args.cidr_filter, args.match, args.cidr_list)
    filter.set_record_mode(args.record, args.from_time, args.until_time)
    """
