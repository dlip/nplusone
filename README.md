# NPlusOne Japanese Sentence Miner

## Description

When creating flashcards from a list of Japanese sentences, one of the best rules to enhance your study is that each new card should only include one new vocabulary word per card (N+1). The advantage being you don't have to try to remember multiple words per card which increases your chance of failing. Another ideal is to learn the most frequent words first.

This is impossible to achieve manually as you have to keep track of known vocabulary and organize the sentences in the correct dependency order, while at the same time taking into consideration the word frequency. This software aims to automate this process, making it much easier to import sentences in bulk. It works great in combination with [subs2srs](http://subs2srs.sourceforge.net/) which can convert subtitles into sentences with snapshots and audio.

## How it works

- Frequency list is loaded so most japanese words get an index from most common to least common, starting at 1 and increasing.
- Known list is loaded if necessary so we can assume these words are already part of your vocabulary.
- The input TSV file is read and each sentences broken up into words.
- Each sentence is scanned and the N+1 order is calculated.
- In order to prioritize the high frequency words the sentences are scanned in multiple passes which can be configured with the `increment` parameter. An `increment` value of 100 will scan for vocab which is in the top 100 of the frequency list, then 200, then 300 etc. The smaller this number the more closely the sentences will follow the freqency order but will increase processing time.
- The output TSV file is written with the following columns:
    - Vocabulary word
    - Vocabulary reading
    - Frequency Index
    - Sentence Reading with cloze tags
    - Fields from the input file


## Installation

- Install [Python 2.7](https://www.python.org/downloads/release/python-2713/)
- Grab the lastest zip from the [release page](https://github.com/dlip/nplusone/releases).
- Unzip the release
- Open the command line inside the release folder and run `python nplusone.py`

### Linux

If you get any errors about mecab or kakasi, you may need to get the version for your distribution.

```
sudo apt install mecab
cp /usr/bin/mecab support/mecab
sudo apt install kakasi
cp /usr/bin/kakasi support/kakasi
```

## Usage

You can get help with the `-h` flag:

```
$ python nplusone.py -h
usage: nplusone.py [-h] [-v] [-c COLUMN] [-i INCREMENT] [-l LIMIT] [-k KNOWN]
                   [-u]
                   input output

positional arguments:
  input                 Path of TSV file to read
  output                Path of TSV file to write

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -c COLUMN, --column COLUMN
                        Column of sentence in input TSV. Default=1.
  -i INCREMENT, --increment INCREMENT
                        Increments to scan frequency of vocabulary.
                        Default=100, Set to 0 to disable.
  -l LIMIT, --limit LIMIT
                        Maximum frequency index of vocabulary to allow.
                        Default=202407, Set to 0 to disable.
  -k KNOWN, --known KNOWN
                        Text file of known vocabulary, one word per line.
                        Default=None
  -u, --update-known    Add new words to known file automatically.
  ```

### Example

`known.tsv`
```
行く
```

`input.tsv`
```
...
てごらん。うん？	メイ　見てごらん。 うん？
...
行くよ。 うん。
...
うん… こりゃ　ススワタリが出たな。
...
```

```
$ python nplusone.py -k known.tsv input.tsv output.tsv
```

`output.tsv`
```
見る	見[み]る	45	メイ　 <cloze>見[み]</cloze>てごらん。うん？	メイ　見てごらん。 うん？
出る	出[で]る	76	うん…こりゃ　ススワタリが <cloze>出[で]</cloze>たな。	うん… こりゃ　ススワタリが出たな。

...
```