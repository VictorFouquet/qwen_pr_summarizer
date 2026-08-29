"""Offline tests for the append-only research log."""

from pr_summarizer.researchlog import ResearchLog, Trial, config_fingerprint, prompt_id


def test_append_and_read_roundtrip(tmp_path):
    log = ResearchLog(tmp_path / "log.jsonl")
    log.append(Trial(trial=1, prompt="p one", metrics={"composite": 0.4}, config_fp="cfg"))
    log.append(Trial(trial=2, prompt="p two", metrics={"composite": 0.8}, config_fp="cfg"))
    records = log.read()
    assert [r["trial"] for r in records] == [1, 2]
    assert records[1]["prompt"] == "p two"
    assert records[0]["prompt_id"] == prompt_id("p one")


def test_best_by_composite(tmp_path):
    log = ResearchLog(tmp_path / "log.jsonl")
    log.append(Trial(trial=1, prompt="a", metrics={"composite": 0.4}))
    log.append(Trial(trial=2, prompt="b", metrics={"composite": 0.9}))
    log.append(Trial(trial=3, prompt="c", metrics={"composite": 0.7}))
    assert log.best()["prompt"] == "b"


def test_next_trial_number(tmp_path):
    log = ResearchLog(tmp_path / "log.jsonl")
    assert log.next_trial_number() == 1
    log.append(Trial(trial=1, prompt="a", metrics={}))
    assert log.next_trial_number() == 2


def test_config_fingerprint_is_stable_and_sensitive():
    a = config_fingerprint({"model": "qwen3:8b", "temperature": 0})
    b = config_fingerprint({"temperature": 0, "model": "qwen3:8b"})  # order-independent
    c = config_fingerprint({"model": "qwen3:8b", "temperature": 0.7})
    assert a == b
    assert a != c
