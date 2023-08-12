## Introduction
**The program could work on both corpus(small / large)**

`search_{large|small}_corpus.py` could build index and search on both corpus(small / large). It will extract the documents, remove stopwords and use porter algorithm to stem the words. Then it will build index and store the data into `cache.json` for future use. For two modes, the program will use BM25 to rank the documents and return the top 15 documents.

`evaluate_{large|small}_corpus.py` could evaluate the result of `search_{large|small}_corpus.py` automatic mode. It will calculate:
- Precision
- Recall
- P@10
- R-precision
- MAP
- bpref

## Quick Start

### File structure

```
.
├── README.md
├── evaluate_large_corpus.py
├── evaluate_small_corpus.py
├── search_large_corpus.py
└── search_small_corpus.py

0 directories, 5 files
```

### How to start

```python
python3 search_{small|large}_corpus.py -m {automatic|interactive}

python3 evaluate_{large|small}_corpus.py
```



