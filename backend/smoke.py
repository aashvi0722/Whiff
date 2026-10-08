from lib.stub import serve


def handler(event, context):
    # STUB: returns the contract sample. Real logic replaces this later.
    return serve(event, "smoke", "smoke_high")
