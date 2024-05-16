import unittest
from main_app_folder.utils.functions import generate_pie_chart, loans_pie_chart, create_bar_chart
from collections import namedtuple
import base64

# Create a mock finance object
Finance = namedtuple('Finance', ['Name', 'Cost'])
Loan = namedtuple('Loan', ['LenderName', 'LoanAmount'])

class TestFunctions(unittest.TestCase):

    def test_generate_pie_chart(self):
        # Mock data
        finances = [
            Finance(Name='Salary', Cost=3000),
            Finance(Name='Freelance', Cost=1500),
            Finance(Name='Investments', Cost=500)
        ]
        
        result = generate_pie_chart(finances)
        self.assertIsInstance(result, str)
        # Check if the result is a valid base64 string
        try:
            decoded_img = base64.b64decode(result)
        except base64.binascii.Error:
            self.fail("Result is not a valid base64 encoded string")

    def test_loans_pie_chart(self):
        # Mock data
        loans = [
            Loan(LenderName='Bank A', LoanAmount=5000),
            Loan(LenderName='Bank B', LoanAmount=3000)
        ]

        result = loans_pie_chart(loans)
        self.assertIsInstance(result, str)
        # Check if the result is a valid base64 string
        try:
            decoded_img = base64.b64decode(result)
        except base64.binascii.Error:
            self.fail("Result is not a valid base64 encoded string")

    def test_create_bar_chart(self):
        # Mock data
        data = [100, 200, 300, 400, 500]
        categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May']

        result = create_bar_chart(data, categories)
        self.assertIsInstance(result, str)
        # Check if the result is a valid base64 string
        try:
            decoded_img = base64.b64decode(result)
        except base64.binascii.Error:
            self.fail("Result is not a valid base64 encoded string")

if __name__ == '__main__':
    unittest.main()
