# raven_core/llm_client.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Dict, List
from pathlib import Path
import os

# --- set CPU/quiet BEFORE importing gpt4all ---
os.environ.setdefault("GGML_NO_CUDA", "1")
os.environ.setdefault("LLAMA_CUBLAS", "0")
os.environ.setdefault("GGML_VERBOSE", "0")

import sys, importlib.util, tkinter as tk

try:
    from gpt4all import GPT4All
except Exception:
    GPT4All = None

@dataclass
class LLMConfig:
    enable: bool = False
    provider: str = "local"
    model_dir: Path = Path.home() / "Raven" / "models"
    model: str = "Phi-3.5-mini-instruct_Uncensored-Q4_K_M.gguf"
    temperature: float = 0.3
    max_tokens: int = 48            # <= even smaller, faster
    n_threads: int = max(2, min(6, (os.cpu_count() or 4)//2))

    def __init__(self) -> None:
        self.enable = str(os.getenv("RAVEN_LLM_ENABLE", "0")).strip().lower() in ("1","true","yes","on")
        self.provider = os.getenv("RAVEN_LLM_PROVIDER", "local").strip().lower()
        self.model_dir = Path(os.environ.get("RAVEN_LLM_PATH", str(self.model_dir)))
        self.model = os.environ.get("RAVEN_LLM_MODEL", self.model)
        self.temperature = float(os.environ.get("RAVEN_LLM_TEMPERATURE", str(self.temperature)))
        self.max_tokens = int(os.environ.get("RAVEN_LLM_MAX_TOKENS", str(self.max_tokens)))
        try:
            self.n_threads = int(os.environ.get("RAVEN_LLM_THREADS", str(self.n_threads)))
        except Exception:
            pass

class LLMClient:
    def __init__(self, cfg: LLMConfig):
        self.cfg = cfg
        self.client = self._init_provider()

    def _init_provider(self):
        if not self.cfg.enable:
            raise RuntimeError("LLM disabled (set RAVEN_LLM_ENABLE=1 to enable).")
        if self.cfg.provider != "local":
            raise RuntimeError(f"Unsupported provider: {self.cfg.provider}. Use 'local'.")

        if GPT4All is None:
            raise RuntimeError("gpt4all package not installed. Run: pip install gpt4all")

        model_path = self.cfg.model_dir / self.cfg.model
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}\nPlace your *.gguf under {self.cfg.model_dir}")

        client = GPT4All(
            model_name=model_path.name,
            model_path=str(self.cfg.model_dir),
            allow_download=False
        )
        try:
            client.model.set_thread_count(self.cfg.n_threads)
        except Exception:
            pass
        return client

    def complete(self, messages: Iterable[Dict[str, str]]) -> str:
        parts: List[str] = []
        for m in messages:
            role = (m.get("role") or "user").strip().upper()
            content = (m.get("content") or "").strip()
            parts.append(f"{role}: {content}")
        prompt = "\n".join(parts) + "\nASSISTANT:"

        try:
            txt = self.client.generate(
                prompt,
                max_tokens=self.cfg.max_tokens,
                temp=self.cfg.temperature,
                top_p=0.9,
                top_k=40,
                repeat_penalty=1.1,
                # Some GPT4All builds accept stop=[]; harmless if ignored:
                stop=["<|end|>", "</s>", "\nUSER:", "\nYou:", "\nUSER >", "ASSISTANT:"]
            )
            out = (txt or "").strip()
            # Hard trim at likely stop markers in case backend didn’t honor stop=
            for mark in ("<|end|>", "</s>", "\nUSER:", "\nYou:", "\nUSER >", "ASSISTANT:"):
                i = out.find(mark)
                if i != -1:
                    out = out[:i].rstrip()
            return out or "I’m here and listening."
        except Exception:
            return "I’m here and listening."
