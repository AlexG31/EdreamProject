import gpt_2_simple as gpt2
import tensorflow as tf
from tensorflow.core.protobuf import rewriter_config_pb2
import os, sys, re
model_name = "117M"
output_file = sys.argv[1]
print('output file: {}'.format(output_file))
print('Using cached model 117M')


def scriptFilter(line):
    nameSet = set(['he',
        'she',
        'who',
        'say',
        'said',
        'says',
        'tell',
        'tells',
        'my',
        'me',
        'his',
        'her',
        'them',
        'they',
        'ours',
        'our',
        'us',
        'jack',
        'rose'
    ])
    patterns = []
    for n in nameSet:
        pat = re.compile(r'\b{}\b'.format(n))
        patterns.append(pat)
    rows = line.split('\n')
    results = []
    for r in rows:
        rl = r.lower()
        for w in nameSet:
            if pat.search(rl) != None:
                results.append(r)
                break
    return results
        

print('-----generate-----')
sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess)
results = gpt2.generate(sess,
length=100,
nsamples=100,
temperature=0.7,
return_as_list=True)

with open(output_file, 'w', encoding='utf8') as fout:
    for line in results:
        rows = scriptFilter(line)
        for r in rows:
            fout.write(r)
            fout.write('\n')
