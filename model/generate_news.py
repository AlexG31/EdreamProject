import gpt_2_simple as gpt2
import tensorflow as tf
from tensorflow.core.protobuf import rewriter_config_pb2
model_name = "117M"
training_data = "../data/training-news.txt"
print('Using cached model 117M')
print('Using training data {}'.format(training_data))


print('-----generate-----')
sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess)
gpt2.generate(sess,
length=100,
nsamples=20,
temperature=0.7)
