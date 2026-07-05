from pathlib import Path

from ollama_evals.config import load_config, resolve_config_path


def test_defaults_when_no_path_and_no_env():
    cfg = load_config(path=None, env={})
    assert cfg.base_url == "http://127.0.0.1:11434/v1"
    assert cfg.temperature == 0.0
    assert cfg.seed == 7
    assert cfg.judge.provider == "local"


def test_env_var_overrides_base_url(tmp_path: Path):
    yaml_file = tmp_path / "models.yaml"
    yaml_file.write_text("base_url: http://127.0.0.1:11434/v1\nmodels: [a, b]\n")
    cfg = load_config(path=yaml_file, env={"OLLAMA_BASE_URL": "http://mini.lan:11434/v1"})
    assert cfg.base_url == "http://mini.lan:11434/v1"


def test_loads_models_and_judge_from_yaml(tmp_path: Path):
    yaml_file = tmp_path / "models.yaml"
    yaml_file.write_text(
        "base_url: http://host:11434/v1\n"
        "defaults: {temperature: 0.2, seed: 42, num_ctx: 4096}\n"
        "models: [qwen2.5-coder:7b, llama3.1:8b]\n"
        "judge: {provider: remote, model: local-judge, remote_model: claude, "
        "remote_api_key_env: ANTHROPIC_API_KEY}\n"
    )
    cfg = load_config(path=yaml_file, env={})
    assert cfg.models == ["qwen2.5-coder:7b", "llama3.1:8b"]
    assert cfg.temperature == 0.2
    assert cfg.seed == 42
    assert cfg.num_ctx == 4096
    assert cfg.judge.provider == "remote"
    assert cfg.judge.remote_model == "claude"
    assert cfg.judge.remote_api_key_env == "ANTHROPIC_API_KEY"


def test_resolve_config_path_prefers_local(tmp_path: Path):
    (tmp_path / "models.yaml").write_text("models: []\n")
    assert resolve_config_path(tmp_path).name == "models.yaml"
    (tmp_path / "models.local.yaml").write_text("models: []\n")
    assert resolve_config_path(tmp_path).name == "models.local.yaml"


def test_resolve_config_path_none_when_absent(tmp_path: Path):
    assert resolve_config_path(tmp_path) is None
