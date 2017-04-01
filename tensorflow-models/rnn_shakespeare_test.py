import os
import requests
import re
import string
import collections
import numpy as np
import matplotlib.pyplot as plt
from utils import to_one_hot
from rnn_lang_model import RNNLangModel


batch_size = 100
training_seq_len = 50


punctuation = string.punctuation
punctuation = ''.join([x for x in punctuation if x not in ['-', "'"]])


def load_text():
    data_dir = 'temp'
    data_file = 'shakespeare.txt'
    model_path = 'shakespeare_model'
    full_model_dir = os.path.join(data_dir, model_path)
    if not os.path.exists(full_model_dir):
        os.makedirs(full_model_dir)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    print('Loading Shakespeare Data')
    if not os.path.isfile(os.path.join(data_dir, data_file)): # check if file is downloaded
        print('Not found, downloading Shakespeare texts from www.gutenberg.org')
        shakespeare_url = 'http://www.gutenberg.org/cache/epub/100/pg100.txt'
        response = requests.get(shakespeare_url) # get Shakespeare text
        shakespeare_file = response.content
        s_text = shakespeare_file.decode('utf-8') # decode binary into string
        s_text = s_text[7675:] # drop first few descriptive paragraphs
        s_text = s_text.replace('\r\n', '') # remove newlines
        s_text = s_text.replace('\n', '') # remove newlines
        with open(os.path.join(data_dir, data_file), 'w') as out_conn: # write to file
            out_conn.write(s_text)
    else:
        with open(os.path.join(data_dir, data_file), 'r') as file_conn: # If file has been saved, load from that file
            s_text = file_conn.read().replace('\n', '')
    return s_text


def build_vocab(word_list, min_word_freq=5):
    word_counts = collections.Counter(word_list)
    word_counts = {key:val for key,val in word_counts.items() if val>min_word_freq}
    words = word_counts.keys()
    word2idx = {key:(idx+1) for idx,key in enumerate(words)} # create word --> index mapping
    word2idx['_unknown'] = 0 # add unknown key --> 0 index
    idx2word = {val:key for key,val in word2idx.items()} # create index --> word mapping
    return(idx2word, word2idx)


def clean_text(s_text):
    s_text = re.sub(r'[{}]'.format(punctuation), ' ', s_text)
    s_text = re.sub('\s+', ' ', s_text ).strip().lower()
    return s_text


def convert_text_to_word_vecs(word_list, word2idx):
    s_text_idx = []
    for word in word_list:
        try:
            s_text_idx.append(word2idx[word])
        except:
            s_text_idx.append(0)
    s_text_idx = np.array(s_text_idx)
    return s_text_idx


def create_batch(s_text_ix):
    # Create batches for each epoch
    num_batches = int(len(s_text_ix)/(batch_size * training_seq_len)) + 1
    # Split up text indices into subarrays, of equal size
    batches = np.array_split(s_text_ix, num_batches)
    # Reshape each split into [batch_size, training_seq_len]
    batches = [np.resize(x, [batch_size, training_seq_len]) for x in batches]
    return batches


if __name__ == '__main__':
    s_text = load_text()

    print('Cleaning Text')
    s_text = clean_text(s_text)

    #char_list = list(s_text) # split up by characters
    word_list = s_text.split()

    print('Building Shakespeare Vocab by Characters')
    idx2word, word2idx = build_vocab(word_list)
    vocab_size = len(idx2word)
    print('Vocabulary Length = {}'.format(vocab_size))
    assert(len(idx2word) == len(word2idx)) # sanity Check

    s_text_idx = convert_text_to_word_vecs(word_list, word2idx)
    
    batch_list = create_batch(s_text_idx)
    X = batch_list
    y = [np.roll(batch, -1, axis=1) for batch in batch_list]
    model = RNNLangModel(n_hidden=128, n_layers=1, vocab_size=vocab_size, seq_len=training_seq_len)
    log = model.fit(X, y, n_epoch=5)
    plt.plot(log['train_acc'])
    plt.show()
