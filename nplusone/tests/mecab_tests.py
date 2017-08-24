# -*- coding: UTF-8 -*-

import unittest
from ..mecab import Mecab

class TestMecab(unittest.TestCase):
 
    def setUp(self):
        self.sut = Mecab()

    def test_returns_tokenized_sentence(self):
        result = self.sut.reading(u'焦げてる')
        self.assertEqual(result[0]['dict_form_reading'], u'焦[こ]げる')

    def test_na_adjectives_dont_have_da_suffix(self):
        result = self.sut.reading(u'安心する')
        self.assertEqual(result[0]['dict_form'], u'安心')
        self.assertEqual(result[0]['dict_form_reading'], u'安心[あんしん]')

    def test_verbs_in_potential_form_resolve_to_dictiory_form(self):
        result = self.sut.reading(u'会える')
        self.assertEqual(result[0]['dict_form'], u'会う')
        self.assertEqual(result[0]['dict_form_reading'], u'会[あ]う')

    def test_katakana_with_dash_is_converted_to_hiragana(self):
        result = self.sut.reading(u'大きい')
        self.assertEqual(result[0]['surface'], u' 大[おお]きい')

        result = self.sut.reading(u'行こう')
        self.assertEqual(result[0]['surface'], u' 行[い]こう')

        result = self.sut.reading(u'苦労')
        self.assertEqual(result[0]['surface'], u' 苦労[くろう]')

        result = self.sut.reading(u'間違い')
        self.assertEqual(result[0]['surface'], u' 間違[まちが]い')

        #リョウコ why is this in output

if __name__ == '__main__':
    unittest.main()