import os
import math
import sys
import getopt
import string
# the path store the corpus
DOCUMENT_PATH = './documents'

# the path store the stopwords list
STOPWORDS_PATH = './files/stopwords.txt'

# the path store the query
QUERY_PATH = './files/queries.txt'

USAGE = '''Usage: search_small_corpus.py -m <mode>
    -m <mode> interactive or automatic
'''


class BM25:
    avg_doc_len = 0 # document's average length
    N = 0 # the number of documents
    docs = dict() # docs[doc_id] store the words frequency in `doc_id`
    frequency = dict() # frequency[word] store the `word` frequency in the corpus
    doc_len = dict() # doc_len[doc_id] store the `doc_id` length
    query = '' # the query we are processing
    k = 1
    b = 0.75

    def __init__(self, avg_doc_len, N, docs, frequency, doc_len, k=1, b=0.75) -> None:
        self.avg_doc_len = avg_doc_len
        self.N = N
        self.docs = docs
        self.frequency = frequency
        self.doc_len = doc_len
        self.k = k
        self.b = b

    def _pre_process_query(self):
        """
            inner method to process the query(remove stopwords, stem...)
        """
        import files.porter as porter
        p = porter.PorterStemmer()
        words = self.query.strip().split()
        for i in range(len(words)):
            if words[i] not in stopwords:
                words[i] = p.stem(words[i].strip().lower())
        self.query = set(words)

    def score(self, query):
        """
            public method to calculate the BM25 score
            parameter: query(str)
        """
        self.query = query
        self._pre_process_query()
        scores = dict()
        for id, doc in self.docs.items():
            score = 0
            for word in self.query:
                """
                    max(0, BM25())
                    I find that if I just use the calculate method from slide,
                    result may appear negative number. The reason is the word is
                    too common in the corpus. It is not reasonable if the score of 
                    a word that actually appear in the document (negative) is lower 
                    than a word that not actually appear (zero). So I forced the 
                    negative score to zero. After a lot of experiments, it is not 
                    effect the result too much. 
                """
                score += max(0,(doc.get(word, 0) * (self.k + 1)) \
                         / (doc.get(word, 0) + self.k * (1 - self.b + self.b * self.doc_len[id] / self.avg_doc_len)) \
                         * (math.log2((N - frequency.get(word, 0) + 0.5) / (frequency.get(word, 0) + 0.5))))
            
            scores[id] = score
        # sort scores
        scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return scores


def preprocess_doc(stopwords, path):
    docs = dict()
    cache = dict() # it is a in-memory cache(different to cache.json), used to cache the stem word
    frequency = dict()
    doc_len = dict()
    import files.porter as porter
    p = porter.PorterStemmer()
    for root, _, files in os.walk(path):
        for file in files:
            if file.isnumeric():
                doc = dict()
                cnt = 0
                with open(os.path.join(root, file), 'r') as f:
                    # read line by line
                    lines = f.readlines()
                    for line in lines:
                        for word in line.strip().split():
                            word = word.strip(string.punctuation) # remove punctuation and special character
                            # word = word.strip('.,:;!?()[]{}')
                            if word.lower() not in stopwords:  # remove stopwords
                                cnt += 1
                                if word in cache:  # use cache to speed up
                                    word = cache[word]
                                else:  # not in cache, stem the word and add to cache
                                    # make sure the word is lower case
                                    tmp = word.lower()
                                    word = p.stem(word.strip().lower())
                                    cache[tmp] = word
                                if word in doc:
                                    doc[word] += 1
                                else:
                                    doc[word] = 1
                                    frequency[word] = frequency.get(word, 0) + 1
                doc_len[int(file)] = cnt
                docs[int(file)] = doc
            else:
                print(f'file name ${file} is not numeric, cannot used as document id')
    return sum(doc_len.values()) / len(doc_len), len(docs), docs, frequency, doc_len


def read_stopwords(path):
    stopwords = set()
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            stopwords.add(line.strip())
    return stopwords


def read_argv():
    """
        read argument from shell to determined interactive mode or automatic mode
        return: is_interactive(bool)
    """
    flag = True
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:")
    except getopt.GetoptError:
        print(USAGE)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(USAGE)
            sys.exit()
        elif opt in ("-m"):
            if arg == 'interactive':
                flag = True
            elif arg == 'automatic':
                flag = False
            else:
                print(USAGE)
                sys.exit(2)
    return flag


if __name__ == '__main__':

    # read the program arguments to decide if is interactive mode
    is_interactive = read_argv()

    # read stopwords from STOPWORDS_PATH and store into set
    stopwords = read_stopwords(STOPWORDS_PATH)

    # detect if the cache file is existed
    if not os.path.exists('cache.json'):
        print('Not found cache index, please wait for indexing...')
        # process the document
        avg_doc_len, N, docs, frequency, doc_len = preprocess_doc(stopwords, DOCUMENT_PATH)
        
        # use json format to store the pre-calculate data
        import json
        with open('cache.json', 'w') as f:
            json.dump({'avg_doc_len': avg_doc_len, 'N': N, 'docs': docs, 'frequency': frequency, 'doc_len': doc_len}, f)
    else:
        print('Loading BM25 index from file, please wait.')
        
        # read from the cache file
        import json
        with open('cache.json', 'r') as f:
            cache = json.load(f)
            avg_doc_len, N, docs, frequency, doc_len = cache['avg_doc_len'], cache['N'], cache['docs'], cache[
                'frequency'], cache['doc_len']

    if is_interactive:
        # user input query in this mode
        # while loop until user input QUIT
        print("Input QUIT to exit the program")
        bm25 = BM25(avg_doc_len, N, docs, frequency, doc_len)
        while True:
            query = input('Enter query: ')
            
            if query.strip() == "QUIT":
                break
            
            scores = bm25.score(query)
            # We only print the first 15 highest score answer
            first15 = scores[:15]
            for index, score in enumerate(first15):
                print(index + 1, score[0], score[1])
            
    else:
        with open(QUERY_PATH, 'r') as f:
            bm25 = BM25(avg_doc_len, N, docs, frequency, doc_len)
            with open('results.txt', 'w') as w:
                lines = f.readlines()
                # every line is a query
                for line in lines:
                    id = line.strip().split()[0]
                    # some query has extra whitespaces
                    query = line.replace(id, '').strip()
                    scores = bm25.score(query)
                    for rank,score in enumerate(scores):
                        # if score is 0, we could skip it. We can assume that the output result are all judged to `relevant`
                        if score[1] == 0.0:
                            continue
                        if rank + 1 > 15:
                            break
                        w.write(id + ' ' + str(score[0])   + ' ' + str(rank+1) + ' ' + str(score[1]) + '\n')
