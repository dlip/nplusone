# -*- coding: UTF-8 -*-

import unittest
import os
from ..parser import Parser
import filecmp

class TestParser(unittest.TestCase):
 
    def setUp(self):
        self.sut = Parser()

    def getTSVPath(self, filename):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', filename + '.tsv')

    def compareTSV(self, tsv_prefix, *args, **kwargs):
        infile = self.getTSVPath(tsv_prefix + '_input')
        outfile = self.getTSVPath(tsv_prefix + '_output')
        result_file = self.getTSVPath(tsv_prefix + '_result')
        known_file = None
        known_file_path = self.getTSVPath(tsv_prefix + '_known')
        if os.path.isfile(known_file_path):
            known_file = known_file_path
        self.sut.parse(infile, outfile, *args, known_file=known_file, **kwargs)
        self.assertTrue(filecmp.cmp(outfile, result_file))

    def test_creates_output_file_with_single_input(self):
        self.compareTSV('basic_add', 5)
    
    def test_nplus_greater_than_one_sentences_are_ignored(self):
        self.compareTSV('nplus_greater_than_one', 5)

    def test_equivalent_sentences_are_ignored(self):
        self.compareTSV('equivalent', 5)

    def test_dependant_sentences_are_resolved(self):
        self.compareTSV('dependant', 5)
    
    def test_frequency_limit_is_observed(self):
        self.compareTSV('frequency_limit', 1, None, 32)

    def test_frequency_increment_adds_sentences_in_order(self):
        self.compareTSV('frequency_increment', 1, 100, None)

    def test_old_vocab_is_ignored_with_known_file(self):
        self.compareTSV('known', 1)

    def test_invalid_sentence_column_throws_exception(self):
        infile = self.getTSVPath('invalid_column_input')
        outfile = self.getTSVPath('invalid_column_output')

        with self.assertRaises(Exception) as context:
            self.sut.parse(infile, outfile, 2)

        with self.assertRaises(Exception) as context:
            self.sut.parse(infile, outfile, 0)

    def test_no_new_sentences_throws_exception(self):
        infile = self.getTSVPath('no_new_sentences_input')
        outfile = self.getTSVPath('no_new_sentences_output')

        with self.assertRaises(Exception) as context:
            self.sut.parse(infile, outfile)


if __name__ == '__main__':
    unittest.main()