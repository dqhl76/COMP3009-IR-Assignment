"""
This file is used to evaluate the result in the large corpus.
The original code is from COMP3009J-corpus-small/evaluate_small_corpus.py,
I just leave comment in the code to explain the difference between the two files.
"""
import math
RESULTS_FILE = 'results.txt'
QRELS_FILE = './files/qrels.txt'


def precision(res, rel):
    sum_precision = 0
    for i in res.keys():
        rel_ret = 0
        for doc_id in res[i]:
            if doc_id in rel[i]:
                rel_ret += 1
        ret = len(res[i])
        precision_res = rel_ret / ret
        sum_precision += precision_res
        # print('Query ID: {}, Precision: {}'.format(i, precision_res))
    return sum_precision / len(res.keys())


def recall(res,rel):
    sum_recall = 0
    for i in res.keys():
        rel_ret = 0
        for doc_id in res[i]:
            if doc_id in rel[i]:
                rel_ret += 1
        rel_len = len(rel[i])
        recall_res = rel_ret / rel_len
        sum_recall += recall_res
        # print('Query ID: {}, Recall: {}'.format(i, recall_res))
    return sum_recall / len(res.keys())


def p_n_internal(single_res, single_rel, n):
    rel_ret = 0
    loop_range = min(len(single_res), n)
    for i in range(loop_range):
        doc_id = single_res[i]
        if doc_id in single_rel:
            rel_ret += 1
    return rel_ret / n


def p_10(res,rel):
    sum_p_10 = 0
    for i in res.keys():
        sum_p_10 += p_n_internal(res[i], rel[i], 10)
    return sum_p_10 / len(res.keys())


def r_precision(res, rel):
    sum_r_precision = 0
    for i in res.keys():
        rel_len = len(rel[i])
        sum_r_precision += p_n_internal(res[i], rel[i], rel_len)
    return sum_r_precision / len(res.keys())


def MAP(res,rel):
    sum_map = 0
    for i in res.keys():
        map = 0
        cnt = 0
        rel_len = len(rel[i])
        for index,doc_id in enumerate(res[i]):
            if doc_id in rel[i]:
                cnt += 1
                map += cnt / (index + 1)
        sum_map += map / rel_len
    return sum_map / len(res.keys())


def bpref(res, rel, unrel):
    sum_bpref = 0
    for i in res.keys():
        nr_cnt = 0 # non-relevant document count
        bpref = 0
        length = len(rel[i])
        for doc_id in res[i]:
            if doc_id in unrel[i]: # if the document is non-relevant
                nr_cnt += 1 # increase the non-relevant document count
            elif doc_id in rel[i]: # if the document is relevant, different to the small corpus
                bpref += max(0, 1 - nr_cnt / length) 
        sum_bpref += bpref / length
    return sum_bpref / len(res.keys())


if __name__ == '__main__':
    results = dict()
    with open(RESULTS_FILE, 'r') as results_file:
        results_file = results_file.readlines()
        for line in results_file:
            query_id, doc_id ,rank, score = line.split(' ')
            if query_id not in results.keys():
                results[query_id] = list()
            results[query_id].append(doc_id.strip())
    

    relevant = dict()
    unrelevant = dict() # add unrelevant dict to store the unrelevant documents
    with open(QRELS_FILE, 'r') as qrels_file:
        qrels_file = qrels_file.readlines()
        for line in qrels_file:
            query_id, _, doc_id, rel = line.replace('  ', ' ').strip().split(' ')
            if rel == '0':
                if query_id not in unrelevant.keys():
                    unrelevant[query_id] = set()
                unrelevant[query_id].add(doc_id.strip())
            else:
                if query_id not in relevant.keys():
                    relevant[query_id] = set()
                relevant[query_id].add(doc_id.strip())
            

    print('Evaluation: {:>10}'.format('results:'))
    print('Precision:    {:>10}'.format(precision(results, relevant)))
    print('Recall:       {:>10}'.format(recall(results, relevant)))
    print('R-precision:  {:>10}'.format(r_precision(results, relevant)))
    print('P@10:         {:>10}'.format(p_10(results, relevant)))
    print('MAP:          {:>10}'.format(MAP(results, relevant)))
    print('bpref:        {:>10}'.format(bpref(results, relevant, unrelevant))) # pass unrelevant dict to the function