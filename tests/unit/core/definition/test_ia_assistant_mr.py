import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import os
from git_ia_assistant.core.definition.ia_assistant_mr import IaAssistantMr

class ConcreteIaAssistantMr(IaAssistantMr):
    def generer_revue_mr(self, diff_path, resume_path):
        return "mocked review"

@pytest.fixture
def mr_assistant():
    return ConcreteIaAssistantMr(
        url_mr="https://github.com/owner/repo/pull/1",
        plateforme="github",
        numero_mr="1",
        out_dir=Path("/tmp")
    )

def test_choisir_prompt_mr_langage_ia_specifique(mr_assistant):
    mr_assistant.langage = "Angular"
    mr_assistant.ia_name = "gemini"
    
    with patch("os.path.exists") as mock_exists:
        # On simule que le prompt spécifique à Gemini pour Angular existe
        mock_exists.side_effect = lambda x: "mr_review_angular_gemini_prompt.md" in x
        
        prompt = mr_assistant._choisir_prompt_mr()
        assert prompt == "review/mr_review_angular_gemini_prompt.md"

def test_choisir_prompt_mr_langage_seul(mr_assistant):
    mr_assistant.langage = "Python"
    mr_assistant.ia_name = "copilot"
    
    with patch("os.path.exists") as mock_exists:
        # On simule qu'aucun prompt spécifique à l'IA n'existe
        mock_exists.return_value = False
        
        prompt = mr_assistant._choisir_prompt_mr()
        assert prompt == "review/mr_review_python_prompt.md"

def test_choisir_prompt_mr_ia_generique(mr_assistant):
    mr_assistant.langage = "Go" # Langage non présent dans _PROMPT_PAR_LANGAGE
    mr_assistant.ia_name = "copilot"
    
    with patch("os.path.exists") as mock_exists:
        # On simule que le prompt générique pour Copilot existe
        mock_exists.side_effect = lambda x: "mr_review_copilot_prompt.md" in x
        
        prompt = mr_assistant._choisir_prompt_mr()
        assert prompt == "review/mr_review_copilot_prompt.md"

def test_choisir_prompt_mr_generique_par_defaut(mr_assistant):
    mr_assistant.langage = "Go"
    mr_assistant.ia_name = "ollama"
    
    with patch("os.path.exists") as mock_exists:
        # On simule qu'aucun fichier spécifique n'existe
        mock_exists.return_value = False
        
        prompt = mr_assistant._choisir_prompt_mr()
        assert prompt == "review/mr_review_prompt.md"

def test_get_version_cible_migration_detectee(mr_assistant):
    mr_assistant.langage = "Angular"
    mr_assistant.migration_info = {
        "detected": True,
        "migrations": [
            {"langage": "angular", "version_target": "20.1.0"}
        ]
    }
    
    version = mr_assistant._get_version_cible()
    assert version == "20"

def test_get_version_cible_sans_migration(mr_assistant):
    mr_assistant.langage = "Python"
    mr_assistant.versions_actuelles = {"python": "3.12.2"}
    
    version = mr_assistant._get_version_cible()
    assert version == "3"

def test_get_version_cible_unknown(mr_assistant):
    mr_assistant.langage = "Unknown"
    mr_assistant.versions_actuelles = {}
    
    version = mr_assistant._get_version_cible()
    assert version == ""
