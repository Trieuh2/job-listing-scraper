import unittest
from utils import *


class TestDataFilteringFunctions(unittest.TestCase):
    def setUp(self):
        self.excluded_keywords = ['senior', 'sr', 'staff', 'principal', 'robotics']

    # ---------------------------------------------------------
    # Tests for exclude_based_on_title function
    # ---------------------------------------------------------
    def test_title_excludes_senior(self):
        title = "senior software engineer"
        self.assertTrue(exclude_based_on_title(self.excluded_keywords, title))

    def test_title_excludes_sr(self):
        title = "sr software engineer"
        self.assertTrue(exclude_based_on_title(self.excluded_keywords, title))
    
    def test_title_does_not_exclude(self):
        title = "software engineer"
        self.assertFalse(exclude_based_on_title(self.excluded_keywords, title))

    def test_title_excludes_mixed_case_senior(self):
        title = "SENIOR software engineer"
        self.assertTrue(exclude_based_on_title(self.excluded_keywords, title))

    def test_title_excludes_with_special_characters(self):
        title = "senior: software engineer"
        self.assertTrue(exclude_based_on_title(self.excluded_keywords, title))

    def test_title_excludes_combined_keyword(self):
        title = "machine learning engineer"
        self.assertTrue(exclude_based_on_title(['machine learning', 'project engineer', 'civil engineer'], title))

    def test_title_does_not_exclude_combined_keyword(self):
        title = "civil eng"
        self.assertFalse(exclude_based_on_title(['machine learning', 'project engineer', 'civil engineer'], title))

class TestURLFunctions(unittest.TestCase):
    # ---------------------------------------------------------
    # Tests for build_indeed_url function
    # ---------------------------------------------------------
    def test_build_indeed_url_all_parameters(self):
        url = build_indeed_url("Software Engineer", "California", "(ENTRY_LEVEL)", "(fulltime)", "7")
        expected_url = "https://www.indeed.com/jobs?q=Software+Engineer&l=California&sc=0kf:explvl(ENTRY_LEVEL)jt(fulltime);&fromage=7"
        self.assertEqual(url, expected_url)

    def test_build_indeed_url_only_position_location(self):
        url = build_indeed_url("Software Engineer", "California", "", "", "")
        expected_url = "https://www.indeed.com/jobs?q=Software+Engineer&l=California"
        self.assertEqual(url, expected_url)

    # ---------------------------------------------------------
    # Tests for get_next_page_url function
    # ---------------------------------------------------------
    def test_get_next_page_url_no_start_specified(self):
        url = "https://www.indeed.com/jobs?q=software+engineer&l=California"
        self.assertEqual(get_next_page_url(url), "https://www.indeed.com/jobs?q=software+engineer&l=California&start=10")

    def test_get_next_page_url_start_specified(self):
        url = "https://www.indeed.com/jobs?q=software+engineer&l=California&start=10"
        self.assertEqual(get_next_page_url(url), "https://www.indeed.com/jobs?q=software+engineer&l=California&start=20")

    # ---------------------------------------------------------
    # Tests for is_valid_indeed_job_link_structure function
    # ---------------------------------------------------------
    def test_is_valid_indeed_job_link_real_job_link(self):
        url1 = "https://www.indeed.com/rc/clk?jk=bb8de57de0baae55&bb=lBZtAEzJGHQbxkjBHBwD-kvm57QidnuC-NUJ03s55g7rDJTDs9V9HEELaoIqEiRSalMTkRUBUTsc8XCnoJeoWs6rZQABuZcrwCqviMfxsBrtlCYJAx1AOA%3D%3D&xkcb=SoBf67M3D0pDJ4AdkD0LbzkdCdPP&fccid=2d499a4c1fa5dde0&vjs=3"
        self.assertTrue(is_valid_indeed_job_link_structure(url1))

    def test_is_invalid_indeed_job_link_company_link(self):
        url1 = "https://www.indeed.com/cmp/Waymo?campaignid=mobvjcmp&from=mobviewjob&tk=1hpkige022ms6000&fromjk=922da2ee875dab33"
        self.assertFalse(is_valid_indeed_job_link_structure(url1))



if __name__ == '__main__':
    unittest.main()