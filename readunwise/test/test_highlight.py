from readunwise.highlight import Highlight


def test_create_highlight_from_clipping():
    clipping = (
        "Never Split the Difference: Negotiating as if Your Life Depended on It (Chris Voss)\n"
        "- Your Highlight at location 1005-1005 | Added on Wednesday, 30 June 2021 20:57:21\n\n"
        "Don't commit to assumptions; instead, view them as hypotheses\n\n\n"
    )

    highlight = Highlight.create(clipping)

    assert highlight is not None
    assert not highlight.is_note
    assert (
        "Never Split the Difference: Negotiating as if Your Life Depended on It (Chris Voss)"
        == highlight.book
    )
    assert (
        "at location 1005-1005 | Added on Wednesday, 30 June 2021 20:57:21"
        == highlight.metadata
    )
    assert (
        "Don't commit to assumptions; instead, view them as hypotheses"
        == highlight.content
    )


def test_create_highlight_from_note_clipping():
    clipping = (
        "Architecture: hgraca (@hgraca)\n"
        "- Your Note on page 24 | location 326 | Added on Saturday, 2 March 2024 11:55:40\n\n"
        "Test note\n\n\n"
    )

    highlight = Highlight.create(clipping)

    assert highlight is not None
    assert highlight.is_note
    assert "Architecture: hgraca (@hgraca)" == highlight.book
    assert (
        "on page 24 | location 326 | Added on Saturday, 2 March 2024 11:55:40"
        == highlight.metadata
    )
    assert "Test note" == highlight.content


def test_bookmark_clipping_is_ignored():
    clipping = (
        "A Clash of Kings (George R. R. Martin)\n"
        "- Your Bookmark on page 717 | location 10990 | Added on Thursday, 16 July 2015 10:16:50\n\n\n"
    )

    highlight = Highlight.create(clipping)

    assert highlight is None
