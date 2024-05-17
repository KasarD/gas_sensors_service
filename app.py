import logging

from typing import Any
from flask import Flask
from flask import request, jsonify
from src.settings import CONFIG
from src.worker import Worker
from src.globals import GLOBALS
from src.combinations.calc import process, get_best_worst_combs
from src.combinations.entities import CombinationsConfig
from src.combinations.plot import max_min_spread, to_base64


WORKER = Worker(2)
app = Flask(__name__)
logger = logging.getLogger("custom")


@app.route("/combinations/calc", methods=["POST"])
def get_combinations():
    if "data" not in request.files:
        return jsonify({"message": "no form data"}), 400
    file = request.files["data"]
    if file.filename == "":
        return jsonify({"message": "empty form data"}), 400
    if file:
        data = file.stream.read().decode("UTF-8")
        # TODO: move to config or to query
        config = CombinationsConfig(2, 10)
        job_uuid = WORKER.commit_job(process, data, config)

    return jsonify({"job_uuid": job_uuid}), 200


def get_job_results(job_uuid: str) -> Any:
    result = GLOBALS.redis.get_job_results(job_uuid)
    logger.debug("result for job %s from redis: %s", job_uuid, result)
    if not result:
        try:
            result = GLOBALS.files.load_job_results(job_uuid)
        except FileNotFoundError as e:
            logger.exception(e)
            result = None
    return result


@app.route("/combinations/result", methods=["GET"])
def get_combinations_results():
    job_uuid = request.args.get("jobUUID")
    if not job_uuid:
        return jsonify({"message": f"bad job_uuid: {job_uuid}"}), 400

    result = get_job_results(job_uuid)
    if not result:
        return jsonify({"message": f"bad result: {result}"}), 500

    return jsonify({"result": result}), 200


# IMAGE
@app.route("/combinations/max-min-spread", methods=["GET"])
def get_combinations_max_min_spread():
    job_uuid = request.args.get("jobUUID")
    if not job_uuid:
        return jsonify({"message": f"bad job_uuid: {job_uuid}"}), 400

    result = get_job_results(job_uuid)
    if not result:
        return jsonify({"message": f"bad result: {result}"}), 500

    b64_image = to_base64(max_min_spread(result))
    return jsonify({"image": b64_image}), 200


@app.route("/combinations/best-worst", methods=["GET"])
def get_combinations_best_worst():
    job_uuid = request.args.get("jobUUID")
    if not job_uuid:
        return jsonify({"message": f"bad job_uuid: {job_uuid}"}), 400

    result = get_job_results(job_uuid)
    if not result:
        return jsonify({"message": f"bad result: {result}"}), 500
    statistic = get_best_worst_combs(result)
    return jsonify(statistic), 200


@app.route("/progress", methods=["GET"])
def get_progress():
    job_uuid = request.args.get("jobUUID")
    if not job_uuid:
        return jsonify({"message": f"bad job_uuid: {job_uuid}"}), 400
    progress = GLOBALS.redis.get_job_progress(job_uuid)
    if not isinstance(progress, float):
        return jsonify({"message": f"bad progress: {progress}"}), 500
    return jsonify({"job_uuid": job_uuid, "progress": progress})


if __name__ == "__main__":
    try:
        app.run("0.0.0.0", 5000)
    finally:
        GLOBALS.shutdown()
        WORKER.shutdown()
