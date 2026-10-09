import io
import sys
from pathlib import Path
import pytest

# Ensure src directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import docs_to_renpy

@pytest.fixture
def mock_file(monkeypatch):
    """Sets a mock StringIO buffer for docs_to_renpy.current_file."""
    buffer = io.StringIO()
    monkeypatch.setattr(docs_to_renpy, "current_file", buffer)
    monkeypatch.setattr(docs_to_renpy, "past_character_name", "[PAST_CHARACTER_NAME]")
    monkeypatch.setattr(docs_to_renpy, "menu_ref_character", None)
    return buffer

# --- Passing Test ---
def test_passing():
    assert 1 == 1

# --- Helper Functions Tests ---

def test_replace_text_rules_bold_and_italic():
    line, bolds = docs_to_renpy.replaceTextRules(r"Here is **bold** and *italic* text \escaped")
    assert "{b}bold{/b}" in line
    assert "{i}italic{/i}" in line
    assert "\\" not in line
    assert bolds == ["bold"]


def test_replace_text_rules_empty_string():
    line, bolds = docs_to_renpy.replaceTextRules("")
    assert line == ""
    assert bolds == []


def test_lowercase_and_underscore():
    result = docs_to_renpy.lowercaseAndUnderscore("Classroom Hallway 01")
    assert result == "classroom_hallway_01"


def test_lowercase_and_underscore_empty():
    assert docs_to_renpy.lowercaseAndUnderscore("") == ""


def test_remove_odd_characters():
    result = docs_to_renpy.removeOddCharacters(r"Scene \#1 with ‘smart’ “quotes” and \slashes")
    assert result == "Scene 1 with smart quotes and slashes"


def test_remove_odd_characters_empty():
    assert docs_to_renpy.removeOddCharacters("") == ""


# --- Parser Regex Tests ---

def test_menu_options_first_option(mock_file):
    line = "1. First choice"
    matched = docs_to_renpy.menuOptions(line)
    output = mock_file.getvalue()
    assert matched is True
    assert "menu:" in output
    assert '"First choice":' in output


def test_menu_options_subsequent_option(mock_file):
    line = "2. Second choice"
    matched = docs_to_renpy.menuOptions(line)
    output = mock_file.getvalue()
    assert matched is True
    assert "menu:" not in output
    assert '"Second choice":' in output


def test_menu_options_invalid_and_empty(mock_file):
    assert docs_to_renpy.menuOptions("Not a menu") is False
    assert docs_to_renpy.menuOptions("") is False
    assert mock_file.getvalue() == ""


def test_background_line(mock_file):
    line = r"\[Background: Classroom\]"
    matched = docs_to_renpy.backgroundLine(line)
    output = mock_file.getvalue()
    assert matched is True
    assert "scene bg classroom" in output


def test_background_line_invalid_and_empty(mock_file):
    assert docs_to_renpy.backgroundLine("Just normal text") is False
    assert docs_to_renpy.backgroundLine("") is False
    assert mock_file.getvalue() == ""


def test_character_line_standard(mock_file):
    line = "**Alice (happy):** Good morning everyone!"
    matched = docs_to_renpy.characterLine(line)
    output = mock_file.getvalue()
    assert matched is True
    assert "show alice happy" in output
    assert 'alice "Good morning everyone!"' in output


def test_character_line_phone(mock_file):
    line = "(Phone)**Bob:** Can you hear me?"
    matched = docs_to_renpy.characterLine(line)
    output = mock_file.getvalue()
    assert matched is True
    assert "show bob silhouette" in output
    assert 'bob "Can you hear me?"' in output


def test_character_line_narration(mock_file):
    line = "**Narration:** It was a quiet morning."
    matched = docs_to_renpy.characterLine(line)
    output = mock_file.getvalue()
    assert matched is True
    assert '"It was a quiet morning."' in output


def test_character_line_invalid_and_empty(mock_file):
    assert docs_to_renpy.characterLine("Random unformatted talk") is False
    assert docs_to_renpy.characterLine("") is False
    assert mock_file.getvalue() == ""


def test_goto_line(mock_file):
    line = r"\[Go to Scene: Hallway \#2\]"
    matched = docs_to_renpy.gotoLine(line)
    output = mock_file.getvalue()
    assert matched is True
    assert "jump hallway_2" in output


def test_goto_line_invalid_and_empty(mock_file):
    assert docs_to_renpy.gotoLine("Go to the store") is False
    assert docs_to_renpy.gotoLine("") is False
    assert mock_file.getvalue() == ""


def test_notebook_line(mock_file):
    line = r'\[Notebook Entry Added: "Secret Note"\]'
    matched = docs_to_renpy.notebookLine(line)
    output = mock_file.getvalue()
    assert matched is True
    assert '$ notebook_entries.append("- Secret Note")' in output


def test_notebook_line_invalid_and_empty(mock_file):
    assert docs_to_renpy.notebookLine("Notebook missing quotes") is False
    assert docs_to_renpy.notebookLine("") is False
    assert mock_file.getvalue() == ""


def test_glossary_line(mock_file):
    line = r'\[Glossary Entry Added: "Visual Novel"\]'
    matched = docs_to_renpy.glossaryLine(line)
    output = mock_file.getvalue()
    assert matched is True
    assert '$ glossary_entries.append("Visual Novel")' in output


def test_glossary_line_invalid_and_empty(mock_file):
    assert docs_to_renpy.glossaryLine("Glossary without quotes") is False
    assert docs_to_renpy.glossaryLine("") is False
    assert mock_file.getvalue() == ""


def test_show_map_line(mock_file):
    line = r"\[Show Map\]"
    matched = docs_to_renpy.showMapLine(line)
    output = mock_file.getvalue()
    assert matched is True
    assert "call screen map()" in output


def test_show_map_line_invalid_and_empty(mock_file):
    assert docs_to_renpy.showMapLine("Show the map please") is False
    assert docs_to_renpy.showMapLine("") is False
    assert mock_file.getvalue() == ""


def test_sound_line(mock_file):
    line = r"\[Sound: Phone rings\]"
    matched = docs_to_renpy.soundLine(line)
    output = mock_file.getvalue()
    assert matched is True
    assert "play sound phone_rings" in output


def test_sound_line_play_music(mock_file):
    line = r"\[play music: Opening Theme\]"
    matched = docs_to_renpy.soundLine(line)
    output = mock_file.getvalue()
    assert matched is True
    assert "play music opening_theme" in output


def test_sound_line_invalid_and_empty(mock_file):
    assert docs_to_renpy.soundLine("Just audio noise") is False
    assert docs_to_renpy.soundLine("") is False
    assert mock_file.getvalue() == ""


def test_sublabel_line(mock_file):
    line = "### Subscene: Bus Talk"
    matched = docs_to_renpy.subLableLine(line)
    output = mock_file.getvalue()
    assert matched is True
    assert "label bus_talk:" in output


def test_sublabel_line_invalid_and_empty(mock_file):
    assert docs_to_renpy.subLableLine("## Scene: Main") is False
    assert docs_to_renpy.subLableLine("") is False
    assert mock_file.getvalue() == ""


def test_comment_line_fallback(mock_file):
    docs_to_renpy.commentLine("This is an unparsed comment line")
    output = mock_file.getvalue()
    assert "# This is an unparsed comment line" in output
