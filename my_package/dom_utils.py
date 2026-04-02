from bs4 import BeautifulSoup, Comment
from typeguard import typechecked  # type: ignore


@typechecked
def go_up(node: object, levels_up: int) -> object:
    """Walk up the parent chain from a node by the requested number of levels.

    Args:
        node (object): Value for node.
        levels_up (int): Value for levels up.

    Returns:
        object: Computed result from this function.
    """
    result = node
    for _ in range(levels_up):
        parent = result.find_parent(True)  # type: ignore[attr-defined]
        if not parent or parent.name in ("html", "body", "[document]"):
            break
        result = parent
    return result


@typechecked
def html_tags_only(html: str) -> str:
    """Return HTML that keeps only tag structure and strips text/comment content.

    Args:
        html (str): HTML content or fragment to process.

    Returns:
        str: String result produced by this function.
    """
    soup = BeautifulSoup(html, "html.parser")

    for text_node in soup.find_all(string=True):
        if isinstance(text_node, Comment):
            text_node.extract()
        else:
            text_node.replace_with("")

    for tag in soup.find_all(True):
        tag.attrs.pop("class", None)

    return str(soup)
