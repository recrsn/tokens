from flask import Flask, jsonify, abort

from tokens.services.scheduler import Scheduler
from tokens.services.token_manager import TokenManager
from tokens.services.token_storage import TokenStorage

app = Flask(__name__)

token_storage = TokenStorage()
scheduler = Scheduler()
token_manager = TokenManager(token_storage, scheduler)

scheduler.start()


@app.route("/tokens/generate", methods=["POST"])
def generate():
    token = token_manager.generate()

    return jsonify(token), 201


@app.route("/tokens/assign")
def assign():
    token = token_manager.assign()

    if not token:
        abort(404)

    return jsonify(token)


@app.route("/tokens/unassign/<token_id>", methods=["POST"])
def unassign(token_id: str):
    token = token_storage.get(token_id)

    if not token:
        abort(404)

    token_manager.unassign(token)

    return "", 204


@app.route("/tokens/<token_id>/keep-alive", methods=["POST"])
def keepalive(token_id: str):
    token = token_storage.get(token_id)

    if not token:
        abort(404)

    token_manager.keep_alive(token)

    return jsonify(token)


@app.route("/tokens")
def get_all():
    return jsonify(list(token_storage.tokens.values()))


@app.route("/tokens/<token_id>", methods=["GET"])
def get(token_id: str):
    token = token_storage.get(token_id)

    if not token:
        abort(404)

    return jsonify(token)


@app.route("/tokens/<token_id>", methods=["DELETE"])
def delete(token_id: str):
    token = token_storage.get(token_id)

    if not token:
        abort(404)

    token_manager.delete(token)

    return "", 204
