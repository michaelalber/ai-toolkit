"""ollama-evals — evaluate and regression-test local Ollama models.

Frontend-agnostic: because Pi, Goose, and Open WebUI all sit on the same Ollama
backend, this harness measures the *model* once at the API level. The result is valid
no matter which frontend drives the model.
"""

__version__ = "0.1.0"
