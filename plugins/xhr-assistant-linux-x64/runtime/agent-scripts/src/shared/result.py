def ok_result(data):
    return {
        "ok": True,
        "data": data,
    }


def error_result(message):
    return {
        "ok": False,
        "error": str(message),
    }
