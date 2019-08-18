import gpt_2_simple as gpt2
import tensorflow as tf
from tensorflow.core.protobuf import rewriter_config_pb2
import sys, logging, time

log_path = sys.argv[1]
logging.basicConfig(filename=log_path, filemode='w', level = logging.INFO)
logger = logging.getLogger('train_model')
logger.info('start training at {}'.format(time.time()))

model_name = "117M"
training_data = "./training-news.txt"
training_steps = 420 # 7 hours
print('Using cached model 117M')
print('Using training data {}'.format(training_data))
#gpt2.download_gpt2(model_name=model_name)   # model is saved into current directory under /models/117M/

sess = gpt2.start_tf_sess()

# print('--Customize gpu configs--')
# config = tf.ConfigProto()
# config.gpu_options.allow_growth = True
# config.gpu_options.per_process_gpu_memory_fraction = 0.8
# config.graph_options.rewrite_options.layout_optimizer = rewriter_config_pb2.RewriterConfig.OFF
# sess = tf.Session(config=config)

gpt2.finetune(sess,
              training_data,
              model_name=model_name,
              steps=training_steps)   # steps is max number of training steps

print('-----generate-----')
gpt2.generate(sess,
temperature=0.7)
