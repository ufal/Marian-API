#parameters 
export MARIAN_PORT=9998
export VERSION=2.1.0
#start the API
MARIAN_SERVER=/home/sellat/marian-dev/build/marian-server
MODEL_PATH=/home/sellat/models_bidirectional/1.0.1/model.npz.best-bleu.npz.decoder.yml
VOCAB_PATH=/home/sellat/models_bidirectional/1.0.1/vocabs.spm
$MARIAN_SERVER --quiet-translation --max-length-factor 2 --mini-batch 1 --cpu-threads 4 -p $MARIAN_PORT -c $MODEL_PATH -v $VOCAB_PATH $VOCAB_PATH &
sleep 15
PYTHONIOENCODING=utf-8 python3 ./api.py --path=/tmp/marian_docker_1s.sock