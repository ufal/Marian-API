#start the API
MARIAN_SERVER=/work/marian-dev/build/marian-server
MODEL_PATH=/work/model/model.npz.best-bleu.npz.decoder.yml
VOCAB_PATH=/work/vocabs/m.spm
MARIAN_PORT=$1
$MARIAN_SERVER --quiet-translation --max-length-factor 2 --mini-batch 1 --cpu-threads 4 -p $MARIAN_PORT -c $MODEL_PATH -v $VOCAB_PATH $VOCAB_PATH &
sleep 15
PYTHONIOENCODING=utf-8 python3 /work/public-api/api.py --path=$2 