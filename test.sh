#!/usr/bin/env bash

TEXT=../data/scientific_corpus__oneDocPerLine.txt
CATEGORY_SEEDCONCEPTS=taxonomy_scientific_corpus.txt
MODEL='ARL'
SEGGED_TEXT_categorized=$TEXT.categorized

source conf.d/autoPhrase.sh

export TEXT_TO_SEG=$TEXT
./phrasal_segmentation.sh
cd -

mkdir -p ../$MODEL
export SEGGED_TEXT=../$MODEL/segmented_text.txt_test
export SEGGED_TEXT_phrase_as_word=$SEGGED_TEXT.phrase_as_word
export SEGGED_TEXT_phrase_as_word_retain_alphanumeric=$SEGGED_TEXT_phrase_as_word.retain_alphanumeric
export SEGGED_TEXT_WORDVEC=../AutoPhrase/$MODEL/wordvec
export SEGGED_TEXT_TFIDF=../AutoPhrase/$MODEL/tfidf

cp ../AutoPhrase/$MODEL/segmentation.txt $SEGGED_TEXT
python segmented2phrase_as_word.py $SEGGED_TEXT $SEGGED_TEXT_phrase_as_word
python retain_alphanumeric.py $SEGGED_TEXT_phrase_as_word $SEGGED_TEXT_phrase_as_word_retain_alphanumeric
python conceptGraphPPR.py $SEGGED_TEXT_phrase_as_word_retain_alphanumeric $CATEGORY_SEEDCONCEPTS $SEGGED_TEXT_categorized $SEGGED_TEXT_WORDVEC $SEGGED_TEXT_TFIDF