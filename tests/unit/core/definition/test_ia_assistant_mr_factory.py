import pytest
from pathlib import Path
from git_ia_assistant.core.definition.ia_assistant_mr_factory import IaAssistantMrFactory
from git_ia_assistant.ia.copilot.ia_copilot_mr import IaCopilotMr
from git_ia_assistant.ia.gemini.ia_gemini_mr import IaGeminiMr
from git_ia_assistant.ia.ollama.ia_ollama_mr import IaOllamaMr

def test_create_mr_instance_copilot():
    instance = IaAssistantMrFactory.create_mr_instance(
        ia="copilot",
        url_mr="https://github.com/owner/repo/pull/1",
        plateforme="github",
        numero_mr="1",
        out_dir=Path("/tmp"),
        langage="Python"
    )
    
    assert isinstance(instance, IaCopilotMr)
    assert instance.ia_name == "copilot"
    assert instance.langage == "Python"

def test_create_mr_instance_gemini_with_kwargs():
    migration_info = {"detected": True, "migrations": []}
    versions_actuelles = {"angular": "20.0.0"}
    
    instance = IaAssistantMrFactory.create_mr_instance(
        ia="gemini",
        url_mr="https://github.com/owner/repo/pull/1",
        plateforme="github",
        numero_mr="1",
        out_dir=Path("/tmp"),
        langage="Angular",
        migration_info=migration_info,
        versions_actuelles=versions_actuelles
    )
    
    assert isinstance(instance, IaGeminiMr)
    assert instance.ia_name == "gemini"
    assert instance.migration_info == migration_info
    assert instance.versions_actuelles == versions_actuelles

def test_create_mr_instance_ollama():
    instance = IaAssistantMrFactory.create_mr_instance(
        ia="ollama",
        url_mr="https://github.com/owner/repo/pull/1",
        plateforme="github",
        numero_mr="1",
        out_dir=Path("/tmp")
    )
    
    assert isinstance(instance, IaOllamaMr)
    assert instance.ia_name == "ollama"
