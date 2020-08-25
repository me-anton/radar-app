body_max_width = 15
body_max_height = 15


def validate_body_str_profile(body: str):
    body_lines = body.splitlines()
    width = len(body_lines[0])
    height = len(body_lines)
    if width > body_max_width or height > body_max_height:
        raise ValueError("Body string is too big")
