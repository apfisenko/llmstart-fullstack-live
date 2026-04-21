from app.infrastructure.llm_assistant import (
    extract_assistant_text_from_choice,
    normalize_completion_message_content,
)


def test_normalize_string_content() -> None:
    assert normalize_completion_message_content({"content": "hi"}) == "hi"


def test_normalize_list_of_text_blocks() -> None:
    msg = {
        "role": "assistant",
        "content": [
            {"type": "text", "text": "Hello "},
            {"type": "text", "text": "world"},
        ],
    }
    assert normalize_completion_message_content(msg) == "Hello world"


def test_normalize_mixed_list() -> None:
    msg = {"content": ["x", {"text": "y", "type": "text"}]}
    assert normalize_completion_message_content(msg) == "xy"


def test_normalize_missing_or_empty() -> None:
    assert normalize_completion_message_content({}) == ""
    assert normalize_completion_message_content({"content": None}) == ""


def test_extract_from_reasoning_string_when_content_empty() -> None:
    choice = {
        "message": {"role": "assistant", "content": "", "reasoning": "Ответ только здесь."},
        "finish_reason": "stop",
    }
    assert extract_assistant_text_from_choice(choice) == "Ответ только здесь."


def test_extract_from_reasoning_details() -> None:
    choice = {
        "message": {
            "role": "assistant",
            "content": None,
            "reasoning_details": [
                {"type": "reasoning.text", "text": "Часть 1"},
                {"type": "reasoning.text", "text": "Часть 2"},
            ],
        }
    }
    assert extract_assistant_text_from_choice(choice) == "Часть 1\n\nЧасть 2"


def test_extract_refusal_fallback() -> None:
    choice = {
        "message": {
            "role": "assistant",
            "content": "",
            "refusal": "Нельзя помочь с этим.",
        }
    }
    assert extract_assistant_text_from_choice(choice) == "Нельзя помочь с этим."


def test_extract_legacy_choice_text() -> None:
    choice = {"message": {"role": "assistant", "content": ""}, "text": "legacy"}
    assert extract_assistant_text_from_choice(choice) == "legacy"
