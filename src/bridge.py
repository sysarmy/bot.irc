import re


BRIDGED_MESSAGE_RE = re.compile(r"^<([^>]+)>\s+(.*)$", re.DOTALL)


def message_identity(nick: str, identity: str, content: str, bridge_nicks: set[str]) -> tuple[str, str]:
    """Return the effective author and content for native or Matterbridge messages."""
    if nick.lower() not in bridge_nicks:
        return identity, content
    match = BRIDGED_MESSAGE_RE.match(content)
    if not match:
        return identity, content
    bridged_author, bridged_content = match.groups()
    return bridged_author, bridged_content
