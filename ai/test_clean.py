from clean import parse_hn_header, strip_html


def test_strip_html_removes_tags():
    assert strip_html("<p>Hello</p>") == "Hello"


def test_strip_html_decodes_codes():
    assert strip_html("Growth &amp; Systems") == "Growth & Systems"


def test_strip_html_fixes_spacing():
    assert strip_html("<p>a</p>   <p>  b  </p>") == "a b"


def test_strip_html_handles_nothing():
    assert strip_html(None) is None
    assert strip_html("") is None


def test_parse_hn_header_normal_post():
    header = parse_hn_header("Acme | ML Engineer | Berlin | REMOTE<p>More text")
    assert header["company"] == "Acme"
    assert header["title"] == "ML Engineer"
    assert header["location"] == "Berlin"
    assert header["remote"] is True


def test_parse_hn_header_no_pipes():
    header = parse_hn_header("Acme is hiring engineers<p>More text")
    assert header["company"] is None
    assert header["title"] is None
    assert header["remote"] is None