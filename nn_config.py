from basics import *
#---------------------------------------------------------------------
# Data Parameters
#---------------------------------------------------------------------
max_vocab_size = {"en" : 200000, "fr" : 200000}

# Special vocabulary symbols - we always put them at the start.
PAD = b"_PAD"
GO = b"_GO"
EOS = b"_EOS"
UNK = b"_UNK"
START_VOCAB = [PAD, GO, EOS, UNK]

PAD_ID = 0
GO_ID = 1
EOS_ID = 2
UNK_ID = 3

NO_ATTN = 0
SOFT_ATTN = 1

print("translating es to en")

model_dir = "mfcc_std_word"
EXP_NAME_PREFIX="callhome"


print("callhome es-en word level configuration")

input_dir = "../../corpora/callhome/uttr_fa_vad_wavs"

speech_dir = os.path.join(input_dir, "mfcc_std")
SPEECH_DIM = 39
MAX_SPEECH_LEN = 400
MIN_SPEECH_LEN = 16
text_data_dict = os.path.join(input_dir, "text_split.dict")

speech_extn = "_fa_vad.std.mfcc"

CHAR_LEVEL = False

NUM_SENTENCES = 17394
# use 90% of the data for training

NUM_TRAINING_SENTENCES = 13137
NUM_MINI_TRAINING_SENTENCES = 13137

ITERS_TO_SAVE = 2

NUM_DEV_SENTENCES = 2476
NUM_MINI_DEV_SENTENCES = 300

NUM_TEST_SENTENCES = 1781

# A total of 11 buckets, with a length range of 7 each, giving total
# BUCKET_WIDTH * NUM_BUCKETS = 77 for e.g.
BUCKET_WIDTH = 3 if not CHAR_LEVEL else 3
NUM_BUCKETS = 14 if not CHAR_LEVEL else 30
TEXT_BUCKETS = [[] for i in range(NUM_BUCKETS)]

MAX_EN_LEN = 100 if not CHAR_LEVEL else 200
# speech bucket width = 25, num_buckets = 32, for a max length of 800
SPEECH_BUCKET_WIDTH = 24
SPEECH_NUM_BUCKETS = 34
SPEECH_BUCKETS = [[] for i in range(SPEECH_NUM_BUCKETS)]

# BATCH_SIZE = 30
# SMALL_BATCH_SIZE = 5
# SWITCH_BATCH_SIZE_INDEX = 11 if SPEECH_NUM_BUCKETS > 10 else SPEECH_NUM_BUCKETS-1

BATCH_SIZE_LOOKUP = {}

# for i in range(SPEECH_NUM_BUCKETS):
#     if i < 7:
#         BATCH_SIZE_LOOKUP[i] = 50
#     elif i >= 7 and i<13:
#         BATCH_SIZE_LOOKUP[i] = 20
#     elif i >= 13 and i<20:
#         BATCH_SIZE_LOOKUP[i] = 10
#     elif i>=20 and i<26:
#         BATCH_SIZE_LOOKUP[i] = 4
#     else:
#         BATCH_SIZE_LOOKUP[i] = 2

for i in range(SPEECH_NUM_BUCKETS):
    if i < 7:
        BATCH_SIZE_LOOKUP[i] = 50
    elif i >= 7 and i<13:
        BATCH_SIZE_LOOKUP[i] = 50
    elif i >= 13 and i<20:
        BATCH_SIZE_LOOKUP[i] = 25
    elif i>=20 and i<26:
        BATCH_SIZE_LOOKUP[i] = 25
    else:
        BATCH_SIZE_LOOKUP[i] = 25


# create separate widths for input and output, speech and english words/chars
MAX_PREDICT_LEN = BUCKET_WIDTH*NUM_BUCKETS

vocab_path = os.path.join(input_dir, "vocab.dict" if not CHAR_LEVEL else "char_vocab.dict")
w2i_path = os.path.join(input_dir, "w2i.dict" if not CHAR_LEVEL else "char_w2i.dict")
i2w_path = os.path.join(input_dir, "i2w.dict" if not CHAR_LEVEL else "char_i2w.dict")

text_fname = {"en": os.path.join(input_dir, "train.en"), "fr": os.path.join(input_dir, "speech_train.es")}

dev_fname = {"en": os.path.join(input_dir, "dev.en"), "fr": os.path.join(input_dir, "speech_dev.es")}

test_fname = {"en": os.path.join(input_dir, "test.en"), "fr": os.path.join(input_dir, "speech_test.es")}

EXP_NAME= "{0:s}_callhome_es_en".format(EXP_NAME_PREFIX)

speech_bucket_data_fname = os.path.join(model_dir, "speech_buckets.dict")

bucket_data_fname = os.path.join(model_dir, "buckets_{0:d}.list" if not CHAR_LEVEL else "buckets_{0:d}_char.list")

if os.path.exists(w2i_path):
    w2i = pickle.load(open(w2i_path, "rb"))
    i2w = pickle.load(open(i2w_path, "rb"))
    vocab = pickle.load(open(vocab_path, "rb"))
    vocab_size_en = min(len(i2w["en"]), max_vocab_size["en"])
    vocab_size_fr = min(len(i2w["fr"]), max_vocab_size["fr"])
    print("vocab size, en={0:d}, fr={1:d}".format(vocab_size_en, vocab_size_fr))

num_layers_enc = 4
num_layers_dec = 2
use_attn = SOFT_ATTN
hidden_units = 512

NUM_EPOCHS = 10

gpuid = 0

load_existing_model = True

xp = cuda.cupy if gpuid >= 0 else np

name_to_log = "{0:d}sen_{1:d}-{2:d}layers_{3:d}units_{4:s}_{5:d}".format(
                                                            NUM_SENTENCES,
                                                            num_layers_enc,
                                                            num_layers_dec,
                                                            hidden_units,
                                                            EXP_NAME,
                                                            use_attn)

log_train_fil_name = os.path.join(model_dir, "train_{0:s}.log".format(name_to_log))
log_dev_fil_name = os.path.join(model_dir, "dev_{0:s}.log".format(name_to_log))
model_fil = os.path.join(model_dir, "seq2seq_{0:s}.model".format(name_to_log))

if not os.path.exists(model_dir):
    os.makedirs(model_dir)

if not os.path.exists(input_dir):
    print("Input folder not found".format(input_dir))

