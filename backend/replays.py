from lib.stub import respond, _events


def handler(event, context):
    return respond(200, {"contract_version": 1, "events": _events()})
