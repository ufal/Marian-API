# Building the Image

To build the image, please follow the steps below:

1. Run the script `automation-scripts/build-image.sh` with the following command:

```
./build-image.sh {model_path} {vocabs_path}
```

Make sure to provide two arguments:

- `{model_path}`: the path to the NMT model
- `{vocabs_path}`: the path to the SentencePiece vocabs model with `.spm` extension

## Starting the Container

After building the image, you can start the container using the following command:

```
docker run \
-p {port_to_bind}:81 \
-e NUM_ENGINES={num_engines} \
--cpus {cpus}\
--memory {memory} \
cuni-multilingual-translation-service:2.1.0
```

Make sure to replace the placeholders with appropriate values:

- `{port_to_bind}`: the port number you want to bind to port 81 in the container
- `{num_engines}`: the number of translation engines you want to run
- `{cpus}`: the number of CPUs you want to allocate to the container
- `{memory}`: the amount of memory you want to allocate to the container

This will start the container with the specified configurations using the `cuni-multilingual-translation-service` image version 2.1.0.
For more details about the API endpoints, please refer to the `client-readme.md` file.

## Contributors
Hashem Sellat  
Mateusz Krubiński  

## License

Unless otherwise stated, our code is released under the MIT License.
