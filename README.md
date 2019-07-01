# Concept Relevance

This repo contains the scripts needed to reproduce the concept based categorizations techniques for scientific publication, i.e., assigning scientific publications into different categories.

## Introduction
The large volume of scientific publications is becoming prohibitive for researchers. According to the prominent [STM report](https://www.stm-assoc.org/2018_10_04_STM_Report_2018.pdf), 
 about 3 million journal articles are being published every year with a 5% annual growth rate. Advanced techniques for
better organizing, navigating, and searching scientific publications are in great demand.
 A first step towards the next-generation management
system for scientific publications is document categorization, i.e., assigning scientific publications into different categories, which provides critical information for many downstream tasks like navigation, search, and trend analysis.

Motivated by the recent development of development of text mining and phrase mining methods, 
 concept based categorizations is proposed to adress the task of scientific document categorization.  The key observation is that scientific publications are
organized based on concepts that bear highly discriminative
information about their categories. For example, a database
paper often involves concepts like “map and reduce” and
“transaction”, while a machine learning paper involves concepts like “statistical inference” and “convergence rate”. 
 
 

## Dependencies

We will take Ubuntu for example.

* python 2.7

```
$ sudo apt-get install python
```
* Python packages dependencies

```
$ sudo pip install -r requirements.txt
```
* The [AutoPhrase](https://github.com/shangjingbo1226/AutoPhrase) for phrasing mining. Please refer to the script if you plan to use custom installation directory.


```
$ cd ..
$ git clone https://github.com/shangjingbo1226/AutoPhrase
$ cd AutoPhrase
$ make
$ # Please refer to AutoPhrase documentation for installation and usage.
```

## Pipeline Overview
The training pipeline is wrapped into a single script `/train.sh`, and one needs to specify the input and output by changing the following variables located at the begining of the script
* ```TEXT```: the input text file
* ```MODEL```: the path to store the model
and to run the training pipeline as

```
$ bash ./train.sh 
```

The testing pipeline is wrapped into a single script `/test.sh`, and one needs to specify the input and output by changing the following variables located at the begining of the script
* ```TEXT```: the input text file
* ```CATEGORY_SEEDCONCEPTS```: one or more set of concepts to query
* ```MODEL```: the path for the stored model you wish to use
* ```SEGGED_TEXT_categorized```: the final output
and to run the testing pipeline as

```
$ bash ./test.sh 
```

## Input Format
* The input files specified by ```TEXT``` for both ```train.sh``` and ```test.sh``` should be one document per line. 
* The categories' seed concepts file ```CATEGORY_SEEDCONCEPTS``` should have each line following the format ```[category name]\t[concept1],[concept2],[concept3]...```, and can contain one or more lines.

## Output Format
* The query relevance output, as specified by the `SEGGED_TEXT_categorized` in the begining of the ```test.sh```, is of the format of [relevance to concept set1], [relevance to concept set2]...


## Hyper-Parameters
The running parameters are located in `conf.d` folder, including `autoPhrase.conf` and `pyConfig.conf`. 

`autoPhrase.conf` contains the parameters for concept extraction and segmentation.

`pyConfig.conf` contains the parameters for all other training steps

### segphrase.conf

```
MIN_SUP=10
```

A hard threshold of raw frequency is specified for frequent phrase mining, which
will generate a candidate set.

```
HIGHLIGHT_MULTI=0.5
```

The threshold for multi-word phrases to be recognized as quality phrases.


```
HIGHLIGHT_SINGLE=0.5
```

The threshold for multi-word phrases to be recognized as quality phrases.

### learning_embedding.conf

```
USE_CONCEPT_GRAPH=1
```
whether to use the concept graph distance algorithm (when set to `1`) or to use the basic query expansion algorithm (when set to `0`) to compute relevance.

```
MIN_NEIGHBOR_SIMILARITY=.6
```
minimum threshold for concept pairs to be considered neighbors in the concept graph

```
MIN_CATEGORY_NEIGHBOR=3
```
minimum number of neighbors that each concept in the query concept set should have

```
MAX_NEIGHBORS=100
```
maximum number of neighbors a concept in the concept will have


### Reference

Please refer to the following paper for further models and evaluation results. If you use this scripts in your own work, please consider citing this:

```
@inproceedings{li2018unsupervised,
  title={Unsupervised neural categorization for scientific publications},
  author={Li, Keqian and Zha, Hanwen and Su, Yu and Yan, Xifeng},
  booktitle={Proceedings of the 2018 SIAM International Conference on Data Mining},
  pages={37--45},
  year={2018},
  organization={SIAM}
}
```
