import math
RESULTS_FILE = 'results.txt'
QRELS_FILE = './files/qrels.txt'


def precision(res, rel):
    """
    calculate precision
    parameters:
        res: dict (key: query_id, value: list of doc_id)
        rel: dict (key: query_id, value: set of doc_id)
    return:
        precision: float
    """
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
    """
    calculate recall
    parameters:
        res: dict (key: query_id, value: list of doc_id)
        rel: dict (key: query_id, value: set of doc_id)
    return:
        recall: float
    """
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
    """
    internal function for calculating P@n, used in p_10 and r_precision
    parameters:
        single_res: list of doc_id
        single_rel: set of doc_id
        n: int (`n` in P@`n`)
    return:
        intermediate result: float
    """
    rel_ret = 0
    loop_range = min(len(single_res), n)
    for i in range(loop_range):
        doc_id = single_res[i]
        if doc_id in single_rel:
            rel_ret += 1
    return rel_ret / n


def p_10(res,rel):
    """
    calculate P@10
    parameters:
        res: dict (key: query_id, value: list of doc_id)
        rel: dict (key: query_id, value: set of doc_id)
    return:
        P@10: float
    """
    sum_p_10 = 0
    for i in res.keys():
        sum_p_10 += p_n_internal(res[i], rel[i], 10)
    return sum_p_10 / len(res.keys())


def r_precision(res, rel):
    """
    calculate R-precision
    parameters:
        res: dict (key: query_id, value: list of doc_id)
        rel: dict (key: query_id, value: set of doc_id)
    return:
        R-precision: float
    """
    sum_r_precision = 0
    for i in res.keys():
        rel_len = len(rel[i])
        sum_r_precision += p_n_internal(res[i], rel[i], rel_len)
    return sum_r_precision / len(res.keys())


def MAP(res,rel):
    """
    calculate MAP
    parameters:
        res: dict (key: query_id, value: list of doc_id)
        rel: dict (key: query_id, value: set of doc_id)
    return:
        MAP: float
    """
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


def bpref(res, rel):
    """
    calculate bpref
    parameters:
        res: dict (key: query_id, value: list of doc_id)
        rel: dict (key: query_id, value: set of doc_id)
    return:
        bpref: float
    """
    sum_bpref = 0
    for i in res.keys():
        nr_cnt = 0 # non-relevant document count
        bpref = 0
        length = len(rel[i])
        for doc_id in res[i]:
            if doc_id not in rel[i]:
                nr_cnt += 1
            else:
                bpref += 1- min(length, nr_cnt)/length
        sum_bpref += bpref / length
    return sum_bpref / len(res.keys())


if __name__ == '__main__':
    results = dict()
    with open(RESULTS_FILE, 'r') as results_file:
        results_file = results_file.readlines()
        for line in results_file:
            query_id, doc_id ,rank, score= line.split(' ')
            if score.strip() == '0.0':
                continue
            if int(query_id) not in results.keys():
                results[int(query_id)] = list()
            results[int(query_id)].append(doc_id.strip())
    
    qrels = dict()
    with open(QRELS_FILE, 'r') as qrels_file:
        qrels_file = qrels_file.readlines()
        for line in qrels_file:
            query_id, _, doc_id, rel = line.replace('  ', ' ').strip().split(' ')
            if int(query_id) not in qrels.keys():
                qrels[int(query_id)] = set()
            qrels[int(query_id)].add(doc_id.strip())

    print('Evaluation: {:>10}'.format('results:'))
    print('Precision:    {:>10}'.format(precision(results, qrels)))
    print('Recall:       {:>10}'.format(recall(results, qrels)))
    print('R-precision:  {:>10}'.format(r_precision(results, qrels)))
    print('P@10:         {:>10}'.format(p_10(results, qrels)))
    print('MAP:          {:>10}'.format(MAP(results, qrels)))
    print('bpref:        {:>10}'.format(bpref(results, qrels)))