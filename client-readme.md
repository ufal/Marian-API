# CUNI Multilingual Translation Service v2.1.0

This text provides details on the deployment and usage of the Machine Translaton service developed by the Charles University for the purpose of the H2020 Welcome project.

## Deployment

The service is implemented as a Docker container and allows to set the number of translation engines running in parallel within the container. It provides RESTful API with JSON data format.

### Requirements

Hardware requirements depend on the number of translation engines (4 engines maximum):

* RAM: 3-12GB
* CPU: 6-18 threads

### Image Specification

| Image | Version | Image File |
|--|--|--|
| cuni-multilingual-translation-service | 2.1.0 | cuni-multilingual-translation-service.tar |

Loading the image:
`docker load < {image_file}` 

Running the container:
``` bash
docker run \
-p {port_to_bind}:81 \
-e NUM_ENGINES={num_engines} \
--cpus {cpus}\
--memory {memory} \
cuni-multilingual-translation-service:2.1.0
```
Note: When starting the container, please wait 10-15 minutes for Marian to get built.
Parameters:

* `port_to_bind` - the local TCP port on `127.0.0.1` of the host machine used to query the translation service running inside docker
* `num_engines` - the number of translation engines running inside the docker container. 
    * Supported values: `1 <= num_engines <= 4`
    * Each of the translation engines requires 4 CPU threads and 3GB of RAM memory. The more engines are running, the higher the translation speed when translating multiple requests in parallel. See table [LINK](#Latency-tests) for the estimates of translation speed. It is recommended to run as many engines as possible. The additional 2 threads are required by the API services.
    * For safety reasons, it is recommended to limit the docker container cpu and RAM memory usage by setting the `--cpus` and `--memory` flags, accorging to the number of used engines. When running one engine, set `{cpus}` to `6` and `{memory}` to `3g` and increase the number of **CPUs by 4** and **RAM memory by 3g** for each additional engine.


## API Endpoints

The service provides three endpoints:

### `POST /translate`

Allows translating the provided text into the target language.
Content type: `application/json; charset=utf-8`.

<h3 id="post__translate-parameters">Parameters</h3>

|Name|Type|Required|Notes|
|---|---|---|---|
|target_language|string|true|ISO 639-3 code of the language you want to translate the text into. Use the `/languages` endpoint to obtain the list of currently supported values. |
|source_language|string|true|ISO 639-3 code indicating source language of your text. Use the `/languages` endpoint to obtain the list of currently supported values. |
|text|string / array of strings|true|Input text. Newline `\n` should be used to separate between sentences in the input text. **Supports translating up to 20 sentences in total, each up to 450 characters**.|


<h3 id="post__translate-responses">Response Codes</h3>

|Status|Meaning|Description|
|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Success.
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation error. Indicates invalid request - missing a required field or sending data exceeding the service limits.
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|Failed to process the request because of an internal problem.
<!-- |502|[Bad Gateway](https://tools.ietf.org/html/rfc7231#section-6.6.3)|Translation failed  - couldn't communicate with the translation engine. 
|504|[Gateway Timeout](https://tools.ietf.org/html/rfc7231#section-6.6.5)|Translation failed - timeout. -->


<h3 id="post__translate-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Value|
|---|---|---|
|translation|string / array of strings|Translation output|
|warning|string|If both source language and target language are supported, but the combination is not officialy supported, a field with relevant warning is provided|

Status Code **422**

|Name|Type|Value|
|---|---|---|
|error|json|Brief description of validation error.|

<h3 id="post__translate-examples">Examples</h3>

Request (string translation):

```bash
curl --request POST '127.0.0.1:LOCAL_PORT/translate' \
--header 'Content-Type: application/json' \
--data-raw \
'{
    "text": "How are you?\nIch habe keine Zeit!",
    "source_language": "deu",
    "target_language": "apc"
}'

```

Response (200):

```json
{
    "translation": "كيف حالك؟\nما عندي وقت!"
}
```

Request (array translation):

```bash
curl --request POST '127.0.0.1:LOCAL_PORT/translate' \
--header 'Content-Type: application/json' \
--data-raw \
'{
    "text": [
            "Πότε θα βρεθούμε σήμερα;",
            "Ελπίζω να νιώθεις καλά!"
            ],
    "source_language": "ell",
    "target_language": "arb",
}'

```

Response (200):

```json
{
    "translation": [
        "متى سنلتقي اليوم؟",
        "أتمنى أن تكوني بخير"
    ]
}
```

Request (missing `target_language`):

```bash
curl --request POST '127.0.0.1:LOCAL_PORT/translate' \
--header 'Content-Type: application/json' \
--data-raw \
'{
    "text": "Ich möchte schlafen."
}'

```

Response (422):

```json
{
    {"error": {"target_language": ["required field"]}}
}
```

Request (too many sentences in one request):

```bash
curl --request POST '127.0.0.1:LOCAL_PORT/translate' \
--header 'Content-Type: application/json' \
--data-raw \
'{
    "text": ["a\nb\nc\nd\n",
             "a\nb\nc\nd\n",
             "a\nb\nc\nd\n",
             "a\nb\nc\nd\n",
             "a\nb\nc\nd\n",
             "a\nb\nc\nd\n"],
    "source_language": "arb",
    "target_language": "deu" 
}'

```

Response (422):

```json
{
    {"error": {"text": ["Too long text in the request. Maximum total number of lines in the whole text: 20."]}}
}
```

<!-- <h3 id="post__translate-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type
|---|---
|» translation|any

*oneOf*

|Name|Type
|---|---
|»» *anonymous*|string

*xor*

|Name|Type
|---|---
|»» *anonymous*|[string]

Status Code **422**

|Name|Type
|---|---
|» error|object

Status Code **500**

|Name|Type
|---|---
|» error|string

<aside class="success">
This operation does not require authentication
</aside> -->


### `GET /status`

Allows checking the status of the service.

<h3 id="get__status-parameters">Parameters</h3>

|Name|Type|Required|Description|
|---|---|---|---|
|full_test|boolean|false|If this key is provided in the query, the service will try to translate a simple text and compare it with the reference translation. 

<h3 id="get__status-responses">Response Codes</h3>

|Status|Meaning|Description|
|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Api is running.|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|Failed to process the request because of an internal problem.|
|503|[Service Unavailable](https://tools.ietf.org/html/rfc7231#section-6.6.3)|An issue preventing the translation engine from working properly.|

<h3 id="get__status-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Value|
|---|---|---|
|api_status|string|"running"|
|version|string|Service version.|

Status Code **503**

|Name|Type|Value|
|---|---|---|
|api_status|string|"not running"|
|error|string|Error message.|

<h3 id="get__status-examples">Examples</h3>

Request (quick heartbeat):

```bash
curl --request GET '127.0.0.1:LOCAL_PORT/status'
```

Response (200):

```json
{
    "api-status": "running",
    "version": "2.1.0"
}
```

Request (full test):

```bash
curl --request GET '127.0.0.1:LOCAL_PORT/status?full_test'
```
Response (200):

```json
{
    "api-status": "running",
    "version": "2.1.0"
}
```

Request:

```bash
curl --request GET '127.0.0.1:LOCAL_PORT/status'
```

Response (503):

```json
{
    "api-status": "not running",
    "error": "Wrong configuration of translation engine."
}
```


### `GET /languages`

Allows getting a list of supported language pairs.



<h3 id="get__languages-responses">Response Codes</h3>

|Status|Meaning|Description
|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Api is running.|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|Failed to process the request because of an internal problem.|

<h3 id="get__languages-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Value|
|---|---|---|
|languages|array of strings|List of supported languages|

<h3 id="get__languages-examples">Examples</h3>

Request:

```bash
curl --request GET '127.0.0.1:LOCAL_PORT/languages'
```

Response (200):

```json
{
    "languages": [
        "eng-arb", "arb-eng", "eng-apc", "apc-eng", "eng-ary",
        "ary-eng", "deu-arb", "arb-deu", "deu-apc", "apc-deu",
        "deu-ary", "ary-deu", "spa-arb", "arb-spa", "spa-apc",
        "apc-spa", "spa-ary", "ary-spa", "fra-arb", "arb-fra",
        "fra-apc", "apc-fra", "fra-ary", "ary-fra", "ell-arb",
        "arb-ell", "ell-apc", "apc-ell", "ell-ary", "ary-ell",
        "cat-arb", "arb-cat", "cat-apc", "apc-cat", "cat-ary",
        "ary-cat", "apc-arb", "arb-apc", "ary-arb", "arb-ary"
    ]
}
```

<!-- <aside class="success">
This operation does not require authentication
</aside> -->

## Note on Error Handling
For every request, the internal webserver might produce two additional errors.
### 502 Bad Gateway
Usually happens when the service is not completely started. Wait for a while (10 seconds), then try again.
```htmlmixed=
<html>
<head><title>502 Bad Gateway</title></head>
<body bgcolor="white">
<center><h1>502 Bad Gateway</h1></center>
<hr><center>nginx/1.14.0 (Ubuntu)</center>
</body>
</html>
```
### 504 Gateway Time-out
Request took more than one minute to get processed.
```htmlmixed=
<html>
<head><title>504 Gateway Time-out</title></head>
<body bgcolor="white">
<center><h1>504 Gateway Time-out</h1></center>
<hr><center>nginx/1.14.0 (Ubuntu)</center>
</body>
</html>
```

## Logging

The event-based logger is accessible via `docker logs`. Each line of the log is composed of several key-value fields, separated with the pipe character ("|"). `CUNI_TRANSLATION_SERVICE` is used in the Source Component field.

### Example

``` bash
time=2022-01-26 11:11:42,749 | lvl=INFO | corr=b90d39748c8692f11fdb1b091f75b471 | trans= | from= | comp=CUNI_TRANSLATION_SERVICE | srv= | subsrv= | op= | msg=GET Status - request.
time=2022-01-26 11:11:42,755 | lvl=INFO | corr=b90d39748c8692f11fdb1b091f75b471 | trans= | from= | comp=CUNI_TRANSLATION_SERVICE | srv= | subsrv= | op= | msg=WebSocket connectiion to translation engine successful.
time=2022-01-26 11:11:52,080 | lvl=INFO | corr=efa40f152fdafeb66514384315826ab1 | trans= | from= | comp=CUNI_TRANSLATION_SERVICE | srv= | subsrv= | op= | msg=Translation request validated successfully.
time=2022-01-26 11:11:52,879 | lvl=INFO | corr=efa40f152fdafeb66514384315826ab1 | trans= | from= | comp=CUNI_TRANSLATION_SERVICE | srv= | subsrv= | op= | msg=Text successfully translated.
```

We also use a second "local" logger to log detailed information about the requests - including the requests body and the translation output, for debugging purposes. Each line here is separated with the "," character and we report only values inside the fields.

### Example

``` bash
2022-01-26 11:12:36,137, f9bda3cc92cfb7b131ef68b03967060f, DEBUG, CUNI_TRANSLATION_SERVICE, RAW: This is a secret message!
2022-01-26 11:12:36,137, f9bda3cc92cfb7b131ef68b03967060f, DEBUG, CUNI_TRANSLATION_SERVICE, PRE_PROCESSED: 2de This is a secret message!
2022-01-26 11:12:36,565, f9bda3cc92cfb7b131ef68b03967060f, DEBUG, CUNI_TRANSLATION_SERVICE, TRANSLATION: Das ist eine geheime Botschaft!
```

Besides that, a certain amount of logs from our internal webserver and translation engine are also passed to `docker logs`. They don't follow any of the two schemas mentioned above.

### Example

``` bash
INFO:aiohttp.access: [26/Jan/2022:11:12:36 +0000] "POST /translate HTTP/1.0" 200 207 "-" "python-requests/2.25.0"

[2022-01-26 11:08:54] Loading model from /work/model/model.npz.best-bleu.npz
```

## Latency tests

In the table below you can find estimates of the translation times. **We measured the total time required to translate 8 sentences, each having roughly 10 words**. We include estimates for three scenarios: 
*    concurrent translation, with 8 clients each requesting a translation of a single sentence in parallel
*    looped-synchronous translation, with a single client requesting translations sentence by sentence, in a loop
*    batch-synchronous translation, with a single client requesting transaltion of 8 sentences at once (using the array variant of the `/translate` endpoint) 


|Scenario|NUM_ENGINES=1|NUM_ENGINES=2|NUM_ENGINES=3|NUM_ENGINES=4|
|---|---|---|---|---|
|concurrent translation|7.17 s ± 39.1 ms |4.74 s ± 243 ms |3.8 s ± 9.21 ms |3.35 s ± 77.8 ms|
|looped-synchronous translation|7.11 s ± 191 ms|7.33 s ± 54.8 ms |7.1 s ± 60 ms|7.16 s ± 139 ms |
|batch-synchronous translation|3.16 s ± 22.7 ms|3.17 s ± 10.4 ms|3.08 s ± 24.5 ms| 3.02 s ± 130 ms|

