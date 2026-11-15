def rewriting_start(send, rewrite):
    """`send` that passes the headers of the response start through `rewrite(status, headers)`, which returns the headers
    to send. `headers` is a list of (name, value) byte pairs."""
    async def send_rewritten(message):
        if message["type"] == "http.response.start":
            message = {**message, "headers": rewrite(message["status"], list(message.get("headers", [])))}
        await send(message)
    return send_rewritten


def values_of(headers, name: str) -> list[str]:
    """The values of a header of the response start, in order."""
    return [value.decode("latin-1") for key, value in headers if key.lower() == name.lower().encode()]


def without(headers, name: str):
    """The headers but those named `name`."""
    return [(key, value) for key, value in headers if key.lower() != name.lower().encode()]


def request_values(scope, name: str) -> list[str]:
    """The values of a header of the request, one per field line."""
    key = name.lower().encode("latin-1")
    return [value.decode("latin-1") for header, value in scope["headers"] if header == key]
