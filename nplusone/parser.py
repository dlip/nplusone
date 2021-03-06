# -*- coding: UTF-8 -*-

import csv
import codecs
import re
import collections
from mecab import Mecab
from utils import utf8String
import os

SENTENCE_COLUMN_DEFAULT = 1
FREQUENCY_INCREMENT_DEFAULT = 100

class Parser(object):

    def __init__(self):
        self.mecab = Mecab()
        

    def parse(self, in_file, out_file, sentence_column=SENTENCE_COLUMN_DEFAULT, frequency_increment=FREQUENCY_INCREMENT_DEFAULT, frequency_limit=None, known_file=None, update_known_file=False, frequency_from_input=False):

        known_vocab = {}
        if known_file:
            with codecs.open(known_file, 'rb', 'utf-8') as f:
                i = 1
                for line in f:
                    known_vocab[line.rstrip('\n').rstrip('\r')] = i
                    i += 1

            
        sentences = []
        sentence_index = sentence_column - 1
        with codecs.open(in_file, 'rb') as in_file_handle:
            reader = csv.reader(in_file_handle, delimiter='\t')
            column_count=len(next(reader))
            if sentence_column > column_count or sentence_column < 1:
                raise Exception('Sentence column {} out of range'.format(sentence_column))
            in_file_handle.seek(0)

            for row in reader:
                if len(row) < sentence_index + 1:
                    continue
                sentence = {}
                sentence['new_tokens'] = {}
                sentence['row'] = row
                sentence['line'] = unicode(row[sentence_index], 'utf-8')
                sentence['tokens'] = self.mecab.reading(sentence['line'])
                
                for token in sentence['tokens']:
                    if 'dict_form' in token and token['dict_form'] not in known_vocab:
                        sentence['new_tokens'][token['dict_form']] = token

                if len(sentence['new_tokens']) > 0:
                    sentences.append(sentence)

        if len(sentences) == 0:
            raise Exception('No new vocabulary found. Either all vocabulary is in the known file or you have used the wrong sentence column.')

        frequency_list = {}
        if frequency_from_input:
            input_frequency = []
            for sentence in sentences:
                for token in sentence['tokens']:
                    if 'dict_form' in token:
                        input_frequency.append(token['dict_form'])
            
            counts = collections.Counter(input_frequency)
            i = 1
            for vocab, _ in counts.most_common():
                frequency_list[vocab] = i
                i += 1
        else:
            frequency_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'support', 'frequency.txt')
            with codecs.open(frequency_file, 'rb', 'utf-8') as f:
                i = 1
                for line in f:
                    frequency_list[line.rstrip('\n').rstrip('\r')] = i
                    i += 1

        frequency_list_length = len(frequency_list)
        if frequency_limit is None or frequency_limit > frequency_list_length:
            frequency_limit = frequency_list_length

        known_file_handle = None
        if known_file and update_known_file:
            known_file_handle = codecs.open(known_file, 'ab', 'utf-8')

        out_file_handle = codecs.open(out_file, "w", "utf-8")
        frequency_index = min(frequency_increment, frequency_list_length)

        while True:
            added_words = {}
            remove_indexes = []
            
            for i in xrange(0, len(sentences)):
                sentence = sentences[i]
                if len(sentence['new_tokens']) == 0:
                    remove_indexes.append(i)
                elif len(sentence['new_tokens']) == 1:
                    dict_form = next(iter(sentence['new_tokens']))
                    
                    # Ignore if this word has been added
                    if dict_form in added_words:
                        remove_indexes.append(i)
                        continue
                    token = sentence['new_tokens'][dict_form]
                    dict_form = token['dict_form']
                    frequency = 0
                    if dict_form in frequency_list:
                        frequency = frequency_list[dict_form]

                    if frequency_index:
                        if frequency == 0 or frequency > frequency_index:
                            continue
                    elif frequency_limit:
                        if frequency == 0 or frequency > frequency_limit:
                            remove_indexes.append(i)
                            continue
                    
                    reading = ''
                    for sentence_token in sentence['tokens']:
                        cloze = 'dict_form' in sentence_token and \
                            sentence_token['dict_form'] == dict_form
                        
                        if cloze: reading += '<cloze>'
                        reading += sentence_token['surface']
                        if cloze: reading += '</cloze>'
                    
                    # Wrap the cloze more closely
                    reading = reading.replace('<cloze> ', ' <cloze>')
                    reading = reading.strip()
                    
                    out_cols = []
                    out_cols.append(token['dict_form'])
                    out_cols.append(token['dict_form_reading'])
                    out_cols.append(str(frequency))
                    out_cols.append(reading)
                    out_cols += map(utf8String, sentence['row'])
                    out_line = '\t'.join(out_cols)
                    out_line += '\n'
                    out_file_handle.write(out_line)

                    if known_file and update_known_file:
                        known_file_handle.write(token['dict_form'] + '\n')

                    added_words[dict_form] = i
                    remove_indexes.append(i)

            if len(added_words) > 0:
                # Remove added from list
                for i in remove_indexes[::-1]:
                    del(sentences[i])

                # Remove added from existing sentences
                for i in xrange(len(sentences) - 1, -1, -1):
                    sentence = sentences[i]
                    for dict_form_reading, _ in added_words.iteritems():
                        sentence['new_tokens'].pop(dict_form_reading, None)
            
            if len(sentences) == 0:
                break
            if frequency_index:
                if not frequency_limit and frequency_index == frequency_list_length:
                    # Allow more passes without any frequency limit
                    frequency_index = None
                    continue
                elif frequency_limit and frequency_index == frequency_limit and len(added_words) == 0:
                   break

                frequency_index += frequency_increment
                if frequency_limit and frequency_index > frequency_limit:
                    frequency_index = frequency_limit
                elif not frequency_limit and frequency_index > frequency_list_length:
                    frequency_index = frequency_list_length

            elif len(added_words) == 0:
                break

        if known_file_handle:
            known_file_handle.close()
        out_file_handle.close()
