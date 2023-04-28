# -*- coding: utf-8 -*-
import argparse
import json

from aiohttp import web
from aiohttp.web import middleware

from helpers import custom_logging
from helpers.custom_validation import CustomValidator
from helpers.marian_ws_connection import MarianWebServerConnection
from helpers.parameters import *
from translation import Translation


@middleware
async def add_request_id_to_log(request, handler):
    x_request_id = request.headers.get("X-Request-ID")
    server_logger_format = "time=%(asctime)s | lvl=%(levelname)s | corr={} | trans= | from= | " \
                           "comp=CUNI_TRANSLATION_SERVICE | srv= | subsrv= | op= | msg=%(message)s".format(
        x_request_id
    )
    local_logger_format = (
        "%(asctime)s, {}, %(levelname)s, CUNI_TRANSLATION_SERVICE, %(message)s".format(
            x_request_id
        )
    )
    custom_logging.update_logger_with_new_format("server_logger", server_logger_format)
    custom_logging.update_logger_with_new_format("local_logger", local_logger_format)
    resp = await handler(request)
    return resp


async def marian_translate(request):
    validator = CustomValidator(
        parameters.api_parameters.lines_limit,
        parameters.api_parameters.char_limit,
        {
            "source_language": {
                "type": "string",
                "allowed": list(SUPPORTED_LANGUAGES),
                "required": True,
            },
            "target_language": {
                "type": "string",
                "allowed": list(SUPPORTED_LANGUAGES),
                "required": True,
            },
            "text": {
                "type": ["string", "list"],
                "required": True,
                "check_with": (
                    "list_of_strings",
                    "limit_char_number",
                    "limit_lines_number",
                ),
            },
        },
    )
    body = await request.text()
    request = json.loads(body)
    if not validator.validate(request):
        server_logger.error("Invalid request: {}".format(
            " ".join("{}: {}".format(_key, validator.errors[_key]) for _key in validator.errors).replace("\n",
                                                                                                         "<endl>")))
        return web.json_response({"error": validator.errors}, status=422)
    server_logger.info("Translation request validated successfully.")
    text_to_translate = request["text"]
    tgt = request["target_language"]
    lang_pair = request["source_language"] + "-" + request["target_language"]
    try:
        if isinstance(text_to_translate, list):
            translated_text = translation_service.batch_translate(
                text_to_translate, tgt
            )
        else:
            translated_text = "".join(
                translation_service.batch_translate([text_to_translate], tgt)
            )
        server_logger.info("Text successfully translated.")
        response_content = {"translation": translated_text}
        if lang_pair not in SUPPORTED_DIRECTIONS:
            response_content["warning"] = f"{lang_pair} direction was not used in the training data - no guarantee of "\
                                          f"performance"
        return web.json_response(response_content)
    except Exception as e:
        server_logger.error("Internal translation error: {}".format(str(e).replace("\n", "<endl>")))
        return web.json_response({"error": str(e)}, status=500)


async def get_status(request):
    server_logger.info("GET Status - request.")
    full_test = request.rel_url.query.get("full_test")

    server_logger.debug("GET Status - performing full test.")
    if full_test is not None:
        try:
            test_translation = translation_service.translate("Hello world!", "deu")
        except Exception as e:
            server_logger.error("Internal translation error: {}".format(str(e).replace("\n", "<endl>")))
            return web.json_response(
                {"api-status": "not running", "error": str(e)}, status=503
            )
        if test_translation != "Hallo Welt!\n":
            server_logger.error("Wrong configuration of translation engine.")
            return web.json_response(
                {
                    "api-status": "not running",
                    "error": "Wrong configuration of translation engine.",
                },
                status=503,
            )

        server_logger.info("GET Status - full test succeded.")
        return web.json_response(
            {"api-status": "running", "version": parameters.api_parameters.version}
        )

    server_logger.info("GET Status - quick test succeded.")
    return web.json_response(
        {"api-status": "running", "version": parameters.api_parameters.version}
    )


async def get_languages(request):
    server_logger.info("GET languages - request.")
    return web.json_response({"languages": SUPPORTED_DIRECTIONS})


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--path")
    args = parser.parse_args()

    server_logger_format = "time=%(asctime)s | lvl=%(levelname)s | corr= | trans= | from= | " \
                           "comp=CUNI_TRANSLATION_SERVICE | srv= | subsrv= | op= | msg=%(message)s"
    local_logger_format = (
        "%(asctime)s,, %(levelname)s, CUNI_TRANSLATION_SERVICE, %(message)s"
    )
    server_logger = custom_logging.setup_custom_logger(
        "server_logger", server_logger_format
    )
    local_logger = custom_logging.setup_custom_logger(
        "local_logger", local_logger_format
    )

    SUPPORTED_LANGUAGES = ["eng", "deu", "spa", "fra", "ell", "cat", "arb", "apc", "ary"]
    eu_langs = ["eng", "deu", "spa", "fra", "ell", "cat"]
    arabic_langs = ["arb", "apc", "ary"]
    SUPPORTED_DIRECTIONS = []

    for _eu_lang in eu_langs:
        for _arabic_lang in arabic_langs:
            SUPPORTED_DIRECTIONS.append(f"{_eu_lang}-{_arabic_lang}")
            SUPPORTED_DIRECTIONS.append(f"{_arabic_lang}-{_eu_lang}")
    for _dialect_lang in ["apc", "ary"]:
        SUPPORTED_DIRECTIONS.append(f"{_dialect_lang}-arb")
        SUPPORTED_DIRECTIONS.append(f"arb-{_dialect_lang}")
    parameters = EnvParameters()
    marian_we_connection = MarianWebServerConnection(parameters.marian_parameters)
    translation_service = Translation(marian_we_connection)
    app = web.Application(middlewares=[add_request_id_to_log])
    app.add_routes(
        [
            web.post("/translate", marian_translate),
            web.get("/status", get_status),
            web.get("/languages", get_languages),
        ]
    )
    web.run_app(app, path=args.path)
