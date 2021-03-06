from builtins import ResourceWarning
import unittest
import dkb2homebank
import os
import warnings

class DKB2HomebankTest(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

    def testShouldConvertCashFile(self):
        dkb2homebank.convertDkbCash('testfiles/cash.csv')
        lineNumber = sum(1 for line in open('cashHomebank.csv'))
        self.assertEqual(lineNumber, 3)

    def testShouldConvertVisaFile(self):
        dkb2homebank.convertVisa('testfiles/visa.csv')
        lineNumber = sum(1 for line in open('visaHomebank.csv'))
        self.assertEqual(lineNumber, 5)

    def testShouldConvertVisaFileWithRange(self):
        dkb2homebank.convertVisa('testfiles/visaRange.csv')
        lineNumber = sum(1 for line in open('visaHomebank.csv'))
        self.assertEqual(lineNumber, 4)

    def tearDown(self):
        self.delete('cashHomebank.csv')
        self.delete('visaHomebank.csv')

    def delete(self, filename):
        if os.path.isfile(filename):
            os.remove(filename)

if __name__ == '__main__':
    unittest.main()
