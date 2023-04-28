FROM nobodyxu/intel-mkl:2020-ubuntu-bionic

ENV NGINX_API_PORT=81 \
    MARIAN_PORT=9988 \
    MARIAN_HOST=localhost \
    CHAR_LIMIT=450 \
    LINES_LIMIT=20
#install required dependencies
RUN apt-get update &&\
    apt-get install -y software-properties-common &&\
    add-apt-repository ppa:deadsnakes/ppa &&\
    apt-get update &&\
    apt-get upgrade -y &&\
    apt-get update --fix-missing &&\
    apt-get install -y supervisor nginx git build-essential libboost-system-dev protobuf-compiler \
 openssl libssl-dev libgoogle-perftools-dev default-jre wget file libboost-all-dev cmake python3.6 python3-pip python3-virtualenv &&\
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1


WORKDIR /work

COPY  make-marian.sh /work/
RUN git clone https://github.com/marian-nmt/marian-dev.git &&\
    cd marian-dev &&\
    git checkout f88ded &&\
    mv /work/make-marian.sh .
    # chmod +x make-marian.sh
    # ./make-marian.sh

# RUN mkdir /work/marian_build
# RUN mv /work/marian-dev/build/marian-server /work/marian_build
# RUN rm -rf /work/marian-dev/

WORKDIR /work

# install API 
ARG VERSION
ENV VERSION=$VERSION 

COPY public-api /work/public-api/
COPY start.sh /work/

COPY model /work/model/
COPY vocabs /work/vocabs/
RUN pip3 install -r public-api/requirements.txt &&\
	chmod +x public-api/start_marian_and_api.sh start.sh &&\
    chown -R www-data:www-data /work/model
 
CMD /work/start.sh
EXPOSE $NGINX_API_PORT
