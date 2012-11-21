#
# Copyright (c) 2006-2012, Prometheus Research, LLC
#


from ..error import Error, Mark
import re
import urllib2

_escape_regexp = re.compile(r"""%(?P<code>[0-9A-Fa-f]{2})?""")

def _escape_replace(match):
    # Two hexdecimal digits that encode a byte value.
    code = match.group('code')
    # Complain if we get `%` not followed by two hexdecimal digits.
    if not code:
        # Prepare the marker object: convert the input to Unicode
        # and adjust the pointers to respect multi-byte characters.
        text = match.string.decode('utf-8', 'ignore')
        start, end = match.span()
        start = len(match.string[:start].decode('utf-8', 'ignore'))
        end = len(match.string[:end].decode('utf-8', 'ignore'))
        mark = Mark(text, start, end)
        raise Error("symbol '%' must be followed by two hexdecimal"
                    " digits", mark)
    # Return the character corresponding to the escape sequence.
    return chr(int(code, 16))


def decode(text):
    """
    Removes transmission artefacts.

    `text`: ``str`` or ``unicode``
        A raw query string.

    *Returns*: ``unicode``
        A processed string; ready for syntax analysis.

    ``%``-encoded octets are decoded; the input text is converted to Unicode.
    """
    assert isinstance(text, (str, unicode))

    # We accept both 8-bit and Unicode strings, but we need to decode %-escaped
    # UTF-8 octets before translating the query to Unicode.
    if isinstance(text, unicode):
        text = text.encode('utf-8')

    # Decode %-encoded UTF-8 octets.
    text = _escape_regexp.sub(_escape_replace, text)

    # Convert the query to Unicode.
    try:
        text = text.decode('utf-8')
    except UnicodeDecodeError, exc:
        # Prepare the error message.
        start = len(text[:exc.start].decode('utf-8', 'ignore'))
        end = len(text[:exc.end].decode('utf-8', 'ignore'))
        mark = Mark(text.decode('utf-8', 'replace'), start, end)
        raise Error("cannot convert a byte sequence %s to UTF-8: %s"
                    % (urllib2.quote(exc.object[exc.start:exc.end]),
                       exc.reason), mark)

    return text


