from __future__ import division
import sys
import networkx as nx
from gensim.models import word2vec
from gensim import corpora, models, similarities
import csv
import numpy as np
import collections
import ConfigParser


cf = ConfigParser.ConfigParser()
cf.read('conf.d/pyConfig.conf')

try:
    MIN_NEIGHBOR_SIMILARITY = cf.getfloat('concept', 'MIN_NEIGHBOR_SIMILARITY')
    MIN_CATEGORY_NEIGHBOR = cf.getint('concept', 'MIN_CATEGORY_NEIGHBOR')
    MAX_NEIGHBORS = cf.getint('concept', 'MAX_NEIGHBORS')
    USE_CONCEPT_GRAPH = cf.getint('concept', 'USE_CONCEPT_GRAPH')
except Exception, e:
    USE_CONCEPT_GRAPH = 0
    MIN_NEIGHBOR_SIMILARITY = .6
    MIN_CATEGORY_NEIGHBOR = 3
    MAX_NEIGHBORS = 100


def flatten(list):
    return [item for sublist in list for item in sublist]


def reverseDict(dict):
    return {v: k for k, v in dict.items()}


file = '../AutoPhrase/ARL/segmentation.txt.phrase_as_word.retain_alphanumeric'
if len(sys.argv) > 1:
    file = sys.argv[1]

category_seedConcepts_file = './taxonomy_scientific_corpus_application.txt'
if len(sys.argv) > 2:
    category_seedConcepts_file = sys.argv[2]

categorization_file = file+'_categorization'
if len(sys.argv) > 3:
    categorization_file = sys.argv[3]

file_concept_label = './tmp/file_concept_label'

file_wordvec = file+'.wordvec'

if len(sys.argv) > 4:
    file = sys.argv[4]

file_tfidf = file+'.tfidf'

if len(sys.argv) > 5:
    file = sys.argv[5]


tsvin = csv.reader(open(category_seedConcepts_file), delimiter='\t')
category_name_list = []
seed_concepts_list = []
for row in tsvin:
    category_name_list.append(row[0].strip())
    seed_concepts_list.append([w.strip().replace(' ', '_') for w in row[1].split(',')])


def get_concept_label_PPR():
    model_concepts = word2vec.Word2Vec.load(file_wordvec)

    ind2label_concepts = model_concepts.wv.index2word
    label2ind_concepts = reverseDict({k: v for k, v in enumerate(ind2label_concepts)})

    def getConceptIDs(seed_concepts, label2ind_concepts):
        l = [label2ind_concepts.get('<phrase>%s</phrase>' % w, label2ind_concepts.get(w)) for w in seed_concepts]
        return [d for d in l if d is not None]

    seed_conceptsAsIds = [getConceptIDs(seed_concepts, label2ind_concepts) for seed_concepts in seed_concepts_list]
    seed_concepts_set = set([ind2label_concepts[i] for i in flatten(seed_conceptsAsIds)])

    ind2label_concepts = [w for w in ind2label_concepts if '_' in w or w in seed_concepts_set]
    label2ind_concepts = reverseDict({k: v for k, v in enumerate(ind2label_concepts)})
    seed_conceptsAsIds = [getConceptIDs(seed_concepts, label2ind_concepts) for seed_concepts in seed_concepts_list]
    seed_concept_sets = [set([ind2label_concepts[i] for i in seed_conceptsAsId]) for seed_conceptsAsId in seed_conceptsAsIds]
    seed_concept_set = set(flatten(seed_concept_sets))
    for ind in seed_concepts_set:
        print ind, 'similar neighbors:', model_concepts.most_similar(ind, topn=10)

    for x in seed_concept_sets:
        print x

    G = nx.Graph()
    for w in ind2label_concepts:
        G.add_node(w, label=w, id=w)
    for w in ind2label_concepts:
        neighbor_wWeights = [(word, score) for word, score in model_concepts.most_similar(w, topn=MAX_NEIGHBORS)]
        # MIN_CATEGORY_NEIGHBOR
        num_neighbors = 0
        for neighbor, weight in neighbor_wWeights:
            if weight < MIN_NEIGHBOR_SIMILARITY:
                if w in seed_concept_set and num_neighbors < MIN_CATEGORY_NEIGHBOR:
                    print w
                    pass
                else:
                    break

            G.add_edge(w, neighbor, weight=weight)
            num_neighbors += 1

    pprs = []
    for category in range(len(seed_conceptsAsIds)):
        personalization_weight = {w: 1 if w in seed_concept_sets[category] else 0 for w in ind2label_concepts}
        pprs.append(nx.pagerank(G, personalization=personalization_weight))
        print 'finished category %s' % category_name_list[category]

    with open (file_concept_label, 'w') as f:
        for i in range(len(ind2label_concepts)):
            f.write('%s:%s\n' % (ind2label_concepts[i], [pprs[category][ind2label_concepts[i]] for category in range(len(category_name_list))]))


def get_concept_label_query_expansion():
    model_concepts = word2vec.Word2Vec.load(file+'.model_wordPruning_dimension200_sg1_max_vocab_size-1')

    ind2label_concepts = model_concepts.wv.index2word
    label2ind_concepts = reverseDict({k:v for k,v in enumerate(ind2label_concepts)})

    def getConceptIDs(seed_concepts, label2ind_concepts):
        l = [label2ind_concepts.get('<phrase>%s</phrase>' % w, label2ind_concepts.get(w)) for w in seed_concepts]
        return [d for d in l if d is not None]

    seed_conceptsAsIds = [getConceptIDs(seed_concepts, label2ind_concepts) for seed_concepts in seed_concepts_list]
    seed_concepts_set = set([ind2label_concepts[i] for i in flatten(seed_conceptsAsIds)])

    ind2label_concepts = [w for w in ind2label_concepts if '_' in w or w in seed_concepts_set]
    label2ind_concepts = reverseDict({k:v for k,v in enumerate(ind2label_concepts)})
    seed_conceptsAsIds = [getConceptIDs(seed_concepts, label2ind_concepts) for seed_concepts in seed_concepts_list]
    seed_concept_sets = [set([ind2label_concepts[i] for i in seed_conceptsAsId]) for seed_conceptsAsId in seed_conceptsAsIds]

    for ind in seed_concepts_set:
        print ind, 'similar neighbors:', model_concepts.most_similar(ind, topn=10)

    # get closest distance for one concept and a set of concepts
    def getDistance_singleWordsSet(word_set, word):
        return max([model_concepts.similarity(w, word) for w in word_set])

    def getDistance_allWordsSets(seed_concept_sets, word):
        return [getDistance_singleWordsSet(ws, word) for ws in seed_concept_sets]

    with open(file_concept_label, 'w') as f:
        for i in range(len(ind2label_concepts)):
            f.write('%s:%s\n' % (ind2label_concepts[i], getDistance_allWordsSets(seed_concept_sets, ind2label_concepts[i])))


def categorize_documents():
    def readSims(file_concept_label):
        word2sims = {}
        with open (file_concept_label) as f:
            for l in f:
                word, label = l.split(':', 1)
                word2sims[word] = eval(label)

        return word2sims

    word2sims = readSims(file_concept_label)

    def readIntoListsOfWords(file):
        return [document.lower().split() for document in open(file).readlines()]
    wordsLists = readIntoListsOfWords(file)

    try:
        corpus = corpora.MmCorpus(file_tfidf+'.corpus')
        dictionary = corpora.Dictionary.load(file_tfidf + '.dict')
        modelTfidf = models.TfidfModel.load(file_tfidf+'.modelTfidf')
    except Exception:
        print 'using new TFIDF model'
        dictionary = corpora.Dictionary(wordsLists)
        corpus = [dictionary.doc2bow(text) for text in wordsLists]
        modelTfidf = models.TfidfModel(corpus)

        corpora.MmCorpus.serialize(file_tfidf + '.corpus', corpus)  # store to disk, for later use
        dictionary.save(file_tfidf + '.dict')  # store the dictionary, for future reference
        modelTfidf.save(file_tfidf+'.modelTfidf')

    document_size = len(wordsLists)

    def getTFIDFWeights(raw_words):
        raw_word2TFIDFweights = { dictionary[word_id]: weight for word_id, weight in modelTfidf[[dictionary.doc2bow(raw_words)]][0] }
        c = collections.Counter(raw_words)
        raw_word2TFIDFweightsTFAdjusted = {word: raw_word2TFIDFweights[word]/c[word] for word in raw_word2TFIDFweights }
        return raw_word2TFIDFweightsTFAdjusted

    # compute tfidf
    def category_inference_score_document_bySUM(wordList, word2sims):
        sims_document = np.zeros(len(category_name_list))
        word2weights = getTFIDFWeights(wordList)

        word_concepts = [word for word in wordList if word in word2sims]
        for word in word_concepts:
            sims_document += np.array(word2sims[word]) * word2weights[word]
        return sims_document

    sims_documents = np.zeros((document_size, len(category_name_list)))

    for i in range(document_size):
        sims_documents[i] = category_inference_score_document_bySUM(wordsLists[i], word2sims)

    with open(categorization_file, 'w') as f:
        for i in range(document_size):
            f.write('%s\n' % (' '.join(['%s' % i for i in sims_documents[i]])))


if __name__ == '__main__':
    if int(USE_CONCEPT_GRAPH):
        get_concept_label_PPR()
    else:
        get_concept_label_query_expansion()

    categorize_documents()