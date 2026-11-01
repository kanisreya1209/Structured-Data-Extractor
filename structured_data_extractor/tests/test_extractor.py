import unittest
from extractor import extract_resume, validate_resume, SAMPLE_RESUME

class ExtractorTests(unittest.TestCase):
    def test_sample_extracts_contact_and_skills(self):
        data = extract_resume(SAMPLE_RESUME.encode(), "sample.txt")
        self.assertEqual(data["contact"]["full_name"], "ARUN KUMAR")
        self.assertEqual(data["contact"]["email"], "arun.kumar@example.com")
        self.assertIn("Python", data["skills"])

    def test_validation_reports_missing_fields(self):
        data = {"contact": {}, "summary": None, "skills": [], "experience": [], "education": []}
        result = validate_resume(data)
        self.assertFalse(result["validation"]["is_valid"])
        self.assertIn("contact.email", result["validation"]["missing_fields"])

if __name__ == "__main__":
    unittest.main()
