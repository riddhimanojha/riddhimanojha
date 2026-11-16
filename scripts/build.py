"""Regenerate every asset in assets/.

    pip install pillow numpy fonttools brotli uharfbuzz
    python scripts/build.py
"""
import header
import eof
import panels

if __name__ == "__main__":
    panels.main_part1()
    import cards
    cards.main(panels.write)
    header.main()
    eof.main()
