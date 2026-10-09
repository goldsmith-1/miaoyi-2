from app.rag import build_messages, needs_emergency_notice, MAX_HISTORY
from app.db import to_vector

CHUNKS = [{"title": "Ginger", "source": "Source A", "content": "Ginger is used for nausea."}]


def test_context_is_numbered_and_question_is_last():
    msgs = build_messages("Does ginger help?", CHUNKS, [])
    assert msgs[0]["role"] == "system" and "[1] Ginger (Source A)" in msgs[0]["content"]
    assert msgs[-1] == {"role": "user", "content": "Does ginger help?"}


def test_history_is_trimmed():
    history = [{"role": "user", "content": str(i)} for i in range(20)]
    msgs = build_messages("q", CHUNKS, history)
    assert len(msgs) == 1 + MAX_HISTORY + 1


def test_emergency_detection_english_and_chinese():
    assert needs_emergency_notice("I have chest pain")
    assert needs_emergency_notice("我胸痛")
    assert not needs_emergency_notice("What tea helps digestion?")


def test_vector_literal():
    assert to_vector([0.1, 0.25]) == "[0.100000,0.250000]"
