"""config.py — load/save of the user-configurable command template."""
from quintic_sim_gfx.gui import config


def test_load_defaults_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "config_dir", lambda: tmp_path)
    c = config.load()
    assert "{poly}" in c["command"]
    assert "quintic_sim" in c["command"]
    assert c["sage"] is True
    assert c["timeout"] > 0


def test_save_load_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "config_dir", lambda: tmp_path)
    c = config.load()
    c["command"] = ".venv/Scripts/python -m quintic_sim_gfx {poly}"
    c["sage"] = False
    config.save(c)
    c2 = config.load()
    assert c2["command"] == ".venv/Scripts/python -m quintic_sim_gfx {poly}"
    assert c2["sage"] is False


def test_corrupt_file_falls_back_to_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "config_dir", lambda: tmp_path)
    (tmp_path / "config.json").write_text("{not json", encoding="utf-8")
    c = config.load()
    assert c["command"] == config.DEFAULTS["command"]


def test_partial_file_merges_over_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "config_dir", lambda: tmp_path)
    (tmp_path / "config.json").write_text('{"sage": false}', encoding="utf-8")
    c = config.load()
    assert c["sage"] is False
    assert "{poly}" in c["command"]  # default kept


def test_unknown_keys_are_ignored(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "config_dir", lambda: tmp_path)
    (tmp_path / "config.json").write_text('{"bogus": 1, "sage": false}', encoding="utf-8")
    c = config.load()
    assert "bogus" not in c
    assert c["sage"] is False
