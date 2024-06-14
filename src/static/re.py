__all__ = [
    "URL_REGEX",
    "INVITE_REGEX",
    "HYPERLINK_REGEX",
    "FAKE_URL_REGEX",
    "FORMATTING_REGEX"
]

import re

URL_REGEX = re.compile(
    r"(http|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"
)
INVITE_REGEX = re.compile(
    r"(https?:\/\/)?(www.)?(discord.(gg|io|me|li)|discordapp.com\/invite)\/[^\s\/]+?(?=\b)"
)
HYPERLINK_REGEX = re.compile(r"\[\S.*?\]\((https|http):\/\/\S.*?\)")
FAKE_URL_REGEX = re.compile(r"\[\S*?\.\S{2,63}\]\((https|http):\/\/\S.*?\)")
FORMATTING_REGEX = re.compile(r"<[:|id|t|@|a:|#]\S+>")