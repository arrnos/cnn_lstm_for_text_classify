import tensorflow as tf
import datetime
import pickle
import numpy as np

from lstm import *
from PreProcess import *

import matplotlib.pyplot as plt
from tensorflow.contrib import learn


global_loss = []
global_accuracy = []


with tf.Graph().as_default():
    session_conf = tf.ConfigProto(
        allow_soft_placement=True,
        log_device_placement=False
    )
    sess = tf.Session(config=session_conf)
    with sess.as_default():
        lstm = Model(num_layers=1,
                     seq_length=1500,
                     embedding_size=128,
                     vocab_size=74680,
                     rnn_size=150,
                     label_size=6)
        global_step = tf.Variable(0, name="global_step", trainable=False)
        optimizer = tf.train.AdamOptimizer(0.001).minimize(lstm.cost, global_step=global_step)
        sess.run(tf.global_variables_initializer())

        def train_step(batch, label):
            feed_dict = {
                lstm.input_data: batch,
                lstm.targets: label,
                lstm.dropout_keep_prob: 0.5
            }
            _, step, loss, accuracy = sess.run(
                [optimizer, global_step, lstm.cost, lstm.accuracy],
                feed_dict=feed_dict)

            time_str = datetime.datetime.now().isoformat()
            print("{}: step {}, loss {}, accuracy {}".format(time_str, step, loss, accuracy))
            global_loss.append(loss)
            global_accuracy.append(accuracy)

        def dev_step(batch, label):
            feed_dict = {
                lstm.input_data: batch,
                lstm.targets: label,
                lstm.dropout_keep_prob: 0.5
            }
            step, loss, accuracy = sess.run([global_step, lstm.cost, lstm.accuracy], feed_dict=feed_dict)
            time_str = datetime.datetime.now().isoformat()
            print("{}: step {}, loss {:g}, accuracy {}".format(time_str, step, loss, accuracy))


        # x_train, y_train, x_dev, y_dev = split_data()
        # batches = batch_iter(list(zip(x_train, y_train)), batch_size=200, num_epochs=50)

        batches = get_batch(3, 300)
        x_dev, y_dev = pickle.load(open("./pkl/test.pkl", "rb"))
        for data in batches:
            x_train, y_train = zip(*data)
            train_step(x_train, y_train)
            current_step = tf.train.global_step(sess, global_step)
            if current_step % 30 == 0:
                print("\nEvaluation:")
                dev_step(x_dev, y_dev)
                print("")

        x = list(range(len(global_loss)))
        plt.plot(x, global_loss, 'r', label="loss")
        plt.xlabel("batches")
        plt.ylabel("loss")
        plt.savefig("loss_modify.png")
        plt.close()

        plt.plot(x, global_accuracy, 'b', label="accuracy")
        plt.xlabel("batches")
        plt.ylabel("accuracy")
        plt.savefig("accuracy.png")
        plt.close()
