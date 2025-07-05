# app.py - Versão: Sorteio Prime (Configurações específicas para a temporada de Prime Day)
# Esta versão inclui:
# - Duas vagas para "Azul".
# - Múltiplas vagas para "Recirculação", "Auditoria", "Shuttle", "Carregamento", "GAP".
# - Funções extras ativadas ("Hatae", "Triagem Hatae", "Curva", "Bipando Hatae") como parte do sorteio geral.
# - Regras de exclusão e probabilidade expandidas para incluir as novas funções extras e grupos conceituais.
# --- TESTE: POSIÇÕES DE CEIA MOVIDAS PARA FUNÇÕES EXTRAS ---
# --- NOVO: NOME DO ARQUIVO EXCEL DINÂMICO ---

import streamlit as st
import random
import collections
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
import io # Para manipular arquivos em memória
import pandas as pd # Para exibir DataFrames no Streamlit

# --- Configuration Data ---
# Core positions for Before/After Dinner shifts (fixed positions in B/C columns)
# ATUALIZADO: Apenas as vagas "1" e "Pesado 1/2" permanecem na Ceia
CORE_POSITIONS = [
    "Recirculação 1",
    "Pesado 1", "Pesado 2",
    "Auditoria 1",
    "Azul 1",
    "Shuttle 1",
    "Carregamento 1",
    "GAP 1"
]

# Activated functions for drawing (sporadic, allocated in G column) - ATUALIZADO
# Inclui as funções extras originais E as posições movidas da CORE_POSITIONS
ACTIVATED_FUNCTIONS = [
    "Hatae - tirar pacote", "Triagem 1", "Triagem 2", "Triagem 3", "Triagem 4",
    "Bipando Hatae 1", "Bipando Hatae 2",
    "Curva - Tirar Pacote",
    "Triagem Hatae 1", "Triagem Hatae 2", "Triagem Hatae 3", "Triagem Hatae 4",
    "Curva 2 - Tirar Pacote",
    # Novas funções extras (movidas de CORE_POSITIONS)
    "Recirculação 2", "Recirculação 3",
    "Auditoria 2", "Auditoria 3",
    "Azul 2",
    "Shuttle 2", "Shuttle 3",
    "Carregamento 2",
    "GAP 2"
]

# Mapeamento de posições conceituais para aplicar a regra "não pode estar em conceituais iguais"
# ATUALIZADO para refletir a nova divisão de CORE e ACTIVATED_FUNCTIONS
CONCEPTUAL_POSITION_GROUPS = {
    "Shuttle": ["Shuttle 1", "Shuttle 2", "Shuttle 3"], # Agora engloba ambas as categorias
    "Auditoria": ["Auditoria 1", "Auditoria 2", "Auditoria 3"], # Engloba ambas as categorias
    "Recirculação": ["Recirculação 1", "Recirculação 2", "Recirculação 3"], # Engloba ambas as categorias
    "Pesado": ["Pesado 1", "Pesado 2"],
    "Azul": ["Azul 1", "Azul 2"], # Engloba ambas as categorias
    "GAP": ["GAP 1", "GAP 2"], # Engloba ambas as categorias
    "Carregamento": ["Carregamento 1", "Carregamento 2"], # Engloba ambas as categorias
    # Novas entradas para as funções ativadas
    "Triagem": ["Triagem 1", "Triagem 2", "Triagem 3", "Triagem 4", "Triagem Hatae 1", "Triagem Hatae 2", "Triagem Hatae 3", "Triagem Hatae 4"],
    "Hatae": ["Hatae - tirar pacote", "Bipando Hatae 1", "Bipando Hatae 2"],
    "Curva": ["Curva - Tirar Pacote", "Curva 2 - Tirar Pacote"]
}

_INVERTED_CONCEPTUAL_GROUPS = {}
for group, positions in CONCEPTUAL_POSITION_GROUPS.items():
    for pos in positions:
        _INVERTED_CONCEPTUAL_GROUPS[pos] = group

ALLOWED_IN_AZUL = ["rinalanc", "leonarsd", "horaroge", "silvnpau", "sousthib"]

# As regras de EXCLUSIONS e INCREASED_PROBABILITY agora devem considerar tanto a posição exata
# quanto o grupo conceitual da posição, conforme definido em CONCEPTUAL_POSITION_GROUPS.
# A lógica de choose_associate_with_rules será ajustada para isso.

EXCLUSIONS = {
    "rinalanc": {
        "GeneralCeia": ["Shuttle 1", "Recirculação 1", "Pesado 1", "Pesado 2", "GAP 1"], # Apenas as posições remanescentes na Ceia
        "GeneralDraw": ["Shuttle 1", "Shuttle 2", "Shuttle 3", "Recirculação 1", "Recirculação 2", "Recirculação 3",
                        "Pesado 1", "Pesado 2", "GAP 1", "GAP 2", # Posições de Ceia e suas "partes extras"
                        "Hatae - tirar pacote", "Triagem 1", "Triagem 2", "Triagem 3", "Triagem 4", # Funções Ativadas
                        "Bipando Hatae 1", "Bipando Hatae 2", "Curva - Tirar Pacote",
                        "Triagem Hatae 1", "Triagem Hatae 2", "Triagem Hatae 3", "Triagem Hatae 4", "Curva 2 - Tirar Pacote",
                        "Auditoria 2", "Auditoria 3", "Azul 2", "Carregamento 2"] # Posições que agora são sorteadas
    },
    "leonarsd": {
        "GeneralCeia": ["Shuttle 1", "Recirculação 1", "Pesado 1", "Pesado 2", "GAP 1"],
        "GeneralDraw": ["Shuttle 1", "Shuttle 2", "Shuttle 3", "Recirculação 1", "Recirculação 2", "Recirculação 3",
                        "Pesado 1", "Pesado 2", "GAP 1", "GAP 2",
                        "Hatae - tirar pacote", "Triagem 1", "Triagem 2", "Triagem 3", "Triagem 4",
                        "Bipando Hatae 1", "Bipando Hatae 2", "Curva - Tirar Pacote",
                        "Triagem Hatae 1", "Triagem Hatae 2", "Triagem Hatae 3", "Triagem Hatae 4", "Curva 2 - Tirar Pacote",
                        "Auditoria 2", "Auditoria 3", "Azul 2", "Carregamento 2"]
    },
    "horaroge": {
        "GeneralCeia": ["Pesado 1", "Pesado 2"],
        "GeneralDraw": ["Pesado 1", "Pesado 2"]
    },
    "silvnpau": {
        "GeneralCeia": ["Carregamento 1"], # Exclusão na ceia
        "GeneralDraw": ["Carregamento 1", "Carregamento 2"] # Exclusão no sorteio
    },
    "sousthib": {
        "GeneralCeia": ["Carregamento 1", "Azul 1"], # Exclusão na ceia
        "GeneralDraw": ["Carregamento 1", "Carregamento 2", "Azul 1", "Azul 2"] # Exclusão no sorteio
    },
    "ferrlucq": {
        "GeneralCeia": ["Azul 1", "Carregamento 1"],
        "GeneralDraw": ["Azul 1", "Azul 2", "Carregamento 1", "Carregamento 2"]
    },
    "ksilsilv": {
        "GeneralCeia": ["Azul 1", "Carregamento 1"],
        "GeneralDraw": ["Azul 1", "Azul 2", "Carregamento 1", "Carregamento 2"]
    },
    "wessouzf": {
        "GeneralCeia": ["Azul 1", "Carregamento 1"],
        "GeneralDraw": ["Azul 1", "Azul 2", "Carregamento 1", "Carregamento 2"]
    },
    "piluanaq": {
        "GeneralCeia": ["Carregamento 1", "Azul 1"], # Exclusão na ceia
        "GeneralDraw": ["Carregamento 1", "Carregamento 2", "Azul 1", "Azul 2"] # Exclusão no sorteio
    },
    "pretojon": {
        "GeneralDraw": { "Azul 1": 3, "Azul 2": 3, "Auditoria 1": 2, "Auditoria 2": 2, "Auditoria 3": 2, "Carregamento 1": 2, "Carregamento 2": 2 }
    },
    "EVAWWELI": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "rabsouza": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "lucenama": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "pedrour": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "ferrlnat": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "doubsant": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "vinichda": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "hjosesil": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "tmarcoso": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "luizsanp": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "nasckluc": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "salucasi": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "mlucneri": {
        "GeneralCeia": [],
        "GeneralDraw": []
    }
}

INCREASED_PROBABILITY = {
    "rinalanc": {
        "GeneralCeia": { "Azul 1": 4, "Auditoria 1": 3, "Carregamento 1": 3 }, # Apenas posições remanescentes na Ceia
        "GeneralDraw": {
            "Azul 1": 4, "Azul 2": 4, "Auditoria 1": 3, "Auditoria 2": 3, "Auditoria 3": 3, "Carregamento 1": 4, "Carregamento 2": 4,
            "Hatae - tirar pacote": 1, "Triagem 1": 1, "Triagem 2": 1, "Triagem 3": 1, "Triagem 4": 1,
            "Bipando Hatae 1": 1, "Bipando Hatae 2": 1, "Curva - Tirar Pacote": 1,
            "Triagem Hatae 1": 1, "Triagem Hatae 2": 1, "Triagem Hatae 3": 1, "Triagem Hatae 4": 1, "Curva 2 - Tirar Pacote": 1,
            # Probabilidades para as posições movidas
            "Recirculação 2": 1, "Recirculação 3": 1, "Auditoria 2": 1, "Auditoria 3": 1,
            "Shuttle 2": 1, "Shuttle 3": 1, "GAP 2": 1
        }
    },
    "leonarsd": {
        "GeneralCeia": { "Azul 1": 4, "Auditoria 1": 3, "Carregamento 1": 3 },
        "GeneralDraw": {
            "Azul 1": 4, "Azul 2": 4, "Auditoria 1": 3, "Auditoria 2": 3, "Auditoria 3": 3, "Carregamento 1": 4, "Carregamento 2": 4,
            "Hatae - tirar pacote": 1, "Triagem 1": 1, "Triagem 2": 1, "Triagem 3": 1, "Triagem 4": 1,
            "Bipando Hatae 1": 1, "Bipando Hatae 2": 1, "Curva - Tirar Pacote": 1,
            "Triagem Hatae 1": 1, "Triagem Hatae 2": 1, "Triagem Hatae 3": 1, "Triagem Hatae 4": 1, "Curva 2 - Tirar Pacote": 1,
            "Recirculação 2": 1, "Recirculação 3": 1, "Auditoria 2": 1, "Auditoria 3": 1,
            "Shuttle 2": 1, "Shuttle 3": 1, "GAP 2": 1
        }
    },
    "horaroge": {
        "GeneralCeia": { "Azul 1": 1, "Carregamento 1": 2, "Auditoria 1": 2, "Recirculação 1": 1, "GAP 1": 1, "Shuttle 1": 1 },
        "GeneralDraw": {
            "Azul 1": 4, "Azul 2": 4, "Carregamento 1": 2, "Carregamento 2": 2,
            "Hatae - tirar pacote": 1, "Triagem 1": 1, "Triagem 2": 1, "Triagem 3": 1, "Triagem 4": 1,
            "Bipando Hatae 1": 1, "Bipando Hatae 2": 1, "Curva - Tirar Pacote": 1,
            "Triagem Hatae 1": 1, "Triagem Hatae 2": 1, "Triagem Hatae 3": 1, "Triagem Hatae 4": 1, "Curva 2 - Tirar Pacote": 1,
            "Recirculação 2": 1, "Recirculação 3": 1, "Auditoria 2": 1, "Auditoria 3": 1,
            "Shuttle 2": 1, "Shuttle 3": 1, "GAP 2": 1
        }
    },
    "silvnpau": {
        "GeneralCeia": { "Azul 1": 1, "Recirculação 1": 1, "Pesado 1": 1, "Pesado 2": 1, "Auditoria 1": 1, "Shuttle 1": 1, "GAP 1": 1 },
        "GeneralDraw": {
            "Azul 1": 4, "Azul 2": 4, "Carregamento 1": 2, "Carregamento 2": 2,
            "Hatae - tirar pacote": 1, "Triagem 1": 1, "Triagem 2": 1, "Triagem 3": 1, "Triagem 4": 1,
            "Bipando Hatae 1": 1, "Bipando Hatae 2": 1, "Curva - Tirar Pacote": 1,
            "Triagem Hatae 1": 1, "Triagem Hatae 2": 1, "Triagem Hatae 3": 1, "Triagem Hatae 4": 1, "Curva 2 - Tirar Pacote": 1,
            "Recirculação 2": 1, "Recirculação 3": 1, "Auditoria 2": 1, "Auditoria 3": 1,
            "Shuttle 2": 1, "Shuttle 3": 1, "GAP 2": 1
        }
    },
    "sousthib": {
        "GeneralCeia": { "Pesado 1": 2, "Pesado 2": 2, "Auditoria 1": 1, "Recirculação 1": 1, "GAP 1": 1, "Shuttle 1": 1 },
        "GeneralDraw": {
            "Azul 1": 4, "Azul 2": 4, "Carregamento 1": 2, "Carregamento 2": 2, "Pesado 1": 2, "Pesado 2": 2,
            "Hatae - tirar pacote": 1, "Triagem 1": 1, "Triagem 2": 1, "Triagem 3": 1, "Triagem 4": 1,
            "Bipando Hatae 1": 1, "Bipando Hatae 2": 1, "Curva - Tirar Pacote": 1,
            "Triagem Hatae 1": 1, "Triagem Hatae 2": 1, "Triagem Hatae 3": 1, "Triagem Hatae 4": 1, "Curva 2 - Tirar Pacote": 1,
            "Recirculação 2": 1, "Recirculação 3": 1, "Auditoria 2": 1, "Auditoria 3": 1,
            "Shuttle 2": 1, "Shuttle 3": 1, "GAP 2": 1
        }
    },
    "ferrlucq": {
        "GeneralCeia": {
            "GAP 1": 2, "Shuttle 1": 2, "Recirculação 1": 2, "Pesado 1": 2, "Pesado 2": 2
        },
        "GeneralDraw": {
            "Pesado 1": 2, "Pesado 2": 2, "GAP 1": 2, "GAP 2": 2, "Recirculação 1": 2, "Recirculação 2": 2, "Recirculação 3": 2,
            "Hatae - tirar pacote": 2, "Triagem 1": 2, "Triagem 2": 2,
            "Triagem 3": 2, "Triagem 4": 2, "Bipando Hatae 1": 2, "Bipando Hatae 2": 2, "Curva - Tirar Pacote": 2,
            "Triagem Hatae 1": 2, "Triagem Hatae 2": 2, "Triagem Hatae 3": 2, "Triagem Hatae 4": 2, "Curva 2 - Tirar Pacote": 2,
            "Shuttle 1": 2, "Shuttle 2": 2, "Shuttle 3": 2, "Auditoria 1": 2, "Auditoria 2": 2, "Auditoria 3": 2
        }
    },
    "ksilsilv": {
        "GeneralCeia": {
            "GAP 1": 2, "Shuttle 1": 2, "Recirculação 1": 2, "Pesado 1": 2, "Pesado 2": 2
        },
        "GeneralDraw": {
            "Pesado 1": 2, "Pesado 2": 2, "GAP 1": 2, "GAP 2": 2, "Recirculação 1": 2, "Recirculação 2": 2, "Recirculação 3": 2,
            "Hatae - tirar pacote": 2, "Triagem 1": 2, "Triagem 2": 2,
            "Triagem 3": 2, "Triagem 4": 2, "Bipando Hatae 1": 2, "Bipando Hatae 2": 2, "Curva - Tirar Pacote": 2,
            "Triagem Hatae 1": 2, "Triagem Hatae 2": 2, "Triagem Hatae 3": 2, "Triagem Hatae 4": 2, "Curva 2 - Tirar Pacote": 2,
            "Shuttle 1": 2, "Shuttle 2": 2, "Shuttle 3": 2, "Auditoria 1": 2, "Auditoria 2": 2, "Auditoria 3": 2
        }
    },
    "pretojon": {
        "GeneralDraw": { "Azul 1": 3, "Azul 2": 3, "Auditoria 1": 2, "Auditoria 2": 2, "Auditoria 3": 2, "Carregamento 1": 2, "Carregamento 2": 2 }
    },
    "wessouzf": {
        "GeneralCeia": { "Recirculação 1": 2, "GAP 1": 3, "Auditoria 1": 1, "Shuttle 1": 1, "Pesado 1": 1, "Pesado 2": 1 },
        "GeneralDraw": {
            "Recirculação 1": 2, "Recirculação 2": 2, "Recirculação 3": 2, "GAP 1": 3, "GAP 2": 3,
            "Hatae - tirar pacote": 1, "Triagem 1": 1, "Triagem 2": 1, "Triagem 3": 1, "Triagem 4": 1,
            "Bipando Hatae 1": 1, "Bipando Hatae 2": 1, "Curva - Tirar Pacote": 1,
            "Triagem Hatae 1": 1, "Triagem Hatae 2": 1, "Triagem Hatae 3": 1, "Triagem Hatae 4": 1, "Curva 2 - Tirar Pacote": 1,
            "Auditoria 1": 1, "Auditoria 2": 1, "Auditoria 3": 1, "Shuttle 1": 1, "Shuttle 2": 1, "Shuttle 3": 1, "Pesado 1": 1, "Pesado 2": 1
        }
    },
    "piluanaq": {
        "GeneralCeia": { "Recirculação 1": 2, "Auditoria 1": 2, "GAP 1": 2, "Pesado 1": 1, "Pesado 2": 1, "Shuttle 1": 1 }, # Apenas posições remanescentes na Ceia
        "GeneralDraw": {
            "Bipando Hatae 1": 2, "Bipando Hatae 2": 2, "Recirculação 1": 2, "Recirculação 2": 2, "Recirculação 3": 2, "Auditoria 1": 2, "Auditoria 2": 2, "Auditoria 3": 2, "GAP 1": 2, "GAP 2": 2, "Pesado 1": 1, "Pesado 2": 1, "Shuttle 1": 1, "Shuttle 2": 1, "Shuttle 3": 1, "Carregamento 1": 1, "Carregamento 2": 1,
            "Hatae - tirar pacote": 1, "Triagem 1": 1, "Triagem 2": 1, "Triagem 3": 1, "Triagem 4": 1, "Curva - Tirar Pacote": 1,
            "Triagem Hatae 1": 1, "Triagem Hatae 2": 1, "Triagem Hatae 3": 1, "Triagem Hatae 4": 1, "Curva 2 - Tirar Pacote": 1
        }
    },
    "EVAWWELI": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "rabsouza": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "lucenama": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "pedrour": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "ferrlnat": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "doubsant": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "vinichda": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "hjosesil": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "tmarcoso": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "luizsanp": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "nasckluc": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "salucasi": {
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "mlucneri": {
        "GeneralCeia": [],
        "GeneralDraw": []
    }
}

CORE_ASSOCIATES_FOR_DINNER = ["rinalanc", "leonarsd"]

# --- Helper Function for Weighted Random Choice with Rules ---
def choose_associate_with_rules(available_associates_in_this_round, position_name, time_slot_context, exclusions, probabilities, additional_exclusions_for_assoc=None):
    
    eligible_associates = []
    weights = []

    for assoc in available_associates_in_this_round:
        current_weight = 1
        is_eligible = True # Assume eligible until an exclusion is found

        # Get conceptual group for the position, if any
        position_conceptual_group = _INVERTED_CONCEPTUAL_GROUPS.get(position_name, None)

        # 1. IMMEDIATE EXCLUSIONS (HIGHEST PRIORITY)

        # Check general exclusion for Azul if associate is not in ALLOWED_IN_AZUL
        if position_name.startswith("Azul") and assoc not in ALLOWED_IN_AZUL:
            is_eligible = False
        
        # Check explicit exclusions from the EXCLUSIONS dictionary
        if is_eligible and assoc in exclusions:
            assoc_exclusions = exclusions[assoc]
            
            # Check if current position_name is in the specific time_slot_context's exclusions
            if time_slot_context in assoc_exclusions and position_name in assoc_exclusions[time_slot_context]:
                is_eligible = False
            # Check if conceptual group is in the specific time_slot_context's exclusions
            elif is_eligible and position_conceptual_group and time_slot_context in assoc_exclusions:
                if any(p in assoc_exclusions[time_slot_context] for p in CONCEPTUAL_POSITION_GROUPS.get(position_conceptual_group, [])):
                    is_eligible = False
            
            # If not excluded by specific context, check if it's in the general context (e.g., GeneralCeia/GeneralDraw)
            if is_eligible: # Only check if not already excluded by a more specific rule
                # Apply GeneralCeia rules for AntesCeia and DepoisCeia contexts
                if "GeneralCeia" in assoc_exclusions and \
                   (time_slot_context.startswith("AntesCeia") or time_slot_context.startswith("DepoisCeia")):
                     if position_name in assoc_exclusions["GeneralCeia"]:
                         is_eligible = False
                     elif position_conceptual_group and any(p in assoc_exclusions["GeneralCeia"] for p in CONCEPTUAL_POSITION_GROUPS.get(position_conceptual_group, [])):
                         is_eligible = False
                # Apply GeneralDraw rules for GeneralDraw context
                elif "GeneralDraw" in assoc_exclusions and time_slot_context == "GeneralDraw":
                     if position_name in assoc_exclusions["GeneralDraw"]:
                         is_eligible = False
                     elif position_conceptual_group and any(p in assoc_exclusions["GeneralDraw"] for p in CONCEPTUAL_POSITION_GROUPS.get(position_conceptual_group, [])):
                         is_eligible = False

        # Apply additional dynamic exclusions (e.g., based on prior allocations in the *same* shift phase)
        if is_eligible and additional_exclusions_for_assoc and assoc in additional_exclusions_for_assoc:
            if position_name in additional_exclusions_for_assoc[assoc]:
                is_eligible = False
            # Check for conceptual group exclusion in dynamic exclusions too
            elif position_conceptual_group and any(p in additional_exclusions_for_assoc[assoc] for p in CONCEPTUAL_POSITION_GROUPS.get(position_conceptual_group, [])):
                is_eligible = False

        # If after ALL exclusions, the associate is still eligible, then apply weights
        if is_eligible:
            # Apply probability weights
            if assoc in probabilities:
                assoc_probabilities = probabilities[assoc]
                # Check specific time slot probability
                if time_slot_context in assoc_probabilities:
                    if position_name in assoc_probabilities[time_slot_context]:
                        current_weight *= assoc_probabilities[time_slot_context][position_name]
                    # Check conceptual group probability for the specific time slot
                    elif position_conceptual_group:
                        # Find the highest weight for any position in the group
                        group_weights = [
                            assoc_probabilities[time_slot_context][p]
                            for p in CONCEPTUAL_POSITION_GROUPS.get(position_conceptual_group, [])
                            if p in assoc_probabilities[time_slot_context]
                        ]
                        if group_weights:
                            current_weight *= max(group_weights) # Apply the strongest probability from the group
                
                # Check general context probability (GeneralCeia/GeneralDraw)
                elif "GeneralCeia" in assoc_probabilities and \
                     (time_slot_context.startswith("AntesCeia") or time_slot_context.startswith("DepoisCeia")):
                    if position_name in assoc_probabilities["GeneralCeia"]:
                        current_weight *= assoc_probabilities["GeneralCeia"][position_name]
                    elif position_conceptual_group:
                        group_weights = [
                            assoc_probabilities["GeneralCeia"][p]
                            for p in CONCEPTUAL_POSITION_GROUPS.get(position_conceptual_group, [])
                            if p in assoc_probabilities["GeneralCeia"]
                        ]
                        if group_weights:
                            current_weight *= max(group_weights)
                
                elif "GeneralDraw" in assoc_probabilities and time_slot_context == "GeneralDraw":
                    if position_name in assoc_probabilities["GeneralDraw"]:
                        current_weight *= assoc_probabilities["GeneralDraw"][position_name]
                    elif position_conceptual_group:
                        group_weights = [
                            assoc_probabilities["GeneralDraw"][p]
                            for p in CONCEPTUAL_POSITION_GROUPS.get(position_conceptual_group, [])
                            if p in assoc_probabilities["GeneralDraw"]
                        ]
                        if group_weights:
                            current_weight *= max(group_weights)
            
            eligible_associates.append(assoc)
            weights.append(current_weight)

    if not eligible_associates:
        return None # No eligible associate for this position

    chosen = random.choices(eligible_associates, weights=weights, k=1)[0]
    return chosen

# --- Allocation Function (Before/After Dinner Shifts) ---
def allocate_dinner_shifts(associates, exclusions, increased_probability, core_associates_for_dinner):
    
    allocated_schedule = {}
    associate_ceia_slots_count = collections.defaultdict(int) 
    antes_ceia_allocations_info = {} 

    shuffled_core_positions = list(CORE_POSITIONS)
    random.shuffle(shuffled_core_positions)

    # --- Phase 1: Allocate AntesCeia positions ---
    antes_ceia_positions_to_fill = [f"AntesCeia - {p}" for p in shuffled_core_positions]
    available_for_antesceia = list(associates) 
    
    # Prioritize core associates for AntesCeia slots
    for core_assoc in core_associates_for_dinner:
        if core_assoc in available_for_antesceia and associate_ceia_slots_count[core_assoc] < 1:
            chosen_position_for_core = None
            
            temp_core_pos_for_antes = list(antes_ceia_positions_to_fill) 
            random.shuffle(temp_core_pos_for_antes)

            for pos_full_name in temp_core_pos_for_antes:
                time_slot, position_name = pos_full_name.split(" - ")
                if not allocated_schedule.get(pos_full_name): 
                    # CRITICAL CALL: Check if the core associate is eligible for this specific position
                    eligible_check = choose_associate_with_rules(
                        [core_assoc], position_name, time_slot, exclusions, increased_probability
                    )
                    if eligible_check == core_assoc:
                        chosen_position_for_core = pos_full_name
                        break
            
            if chosen_position_for_core:
                allocated_schedule[chosen_position_for_core] = core_assoc
                associate_ceia_slots_count[core_assoc] += 1
                
                antes_ceia_allocations_info[core_assoc] = {
                    "exact_position": position_name,
                    "conceptual_group": _INVERTED_CONCEPTUAL_GROUPS.get(position_name, position_name)
                }
                
                available_for_antesceia.remove(core_assoc) 
                antes_ceia_positions_to_fill.remove(chosen_position_for_core) 
            else:
                pass 


    # Fill remaining AntesCeia positions with other available associates
    for full_pos_str in antes_ceia_positions_to_fill:
        if not allocated_schedule.get(full_pos_str): 
            time_slot, position_name = full_pos_str.split(" - ")
            chosen_associate = choose_associate_with_rules(
                available_for_antesceia, position_name, time_slot, exclusions, increased_probability
            )
            if chosen_associate:
                allocated_schedule[full_pos_str] = chosen_associate
                associate_ceia_slots_count[chosen_associate] += 1
                
                antes_ceia_allocations_info[chosen_associate] = {
                    "exact_position": position_name,
                    "conceptual_group": _INVERTED_CONCEPTUAL_GROUPS.get(position_name, position_name)
                }
                
                available_for_antesceia.remove(chosen_associate) 
            else:
                allocated_schedule[full_pos_str] = "(Vazio/Nenhum Associado Elegível)"


    # --- Phase 2: Allocate DepoisCeia positions ---
    depois_ceia_positions_to_fill = [f"DepoisCeia - {p}" for p in shuffled_core_positions]
    
    associates_eligible_for_depois_ceia = []
    for assoc in associates:
        target_slots = 2 if assoc in core_associates_for_dinner else 1
        if associate_ceia_slots_count[assoc] < target_slots:
            associates_eligible_for_depois_ceia.append(assoc)
    
    random.shuffle(associates_eligible_for_depois_ceia) 

    for full_pos_str in depois_ceia_positions_to_fill:
        if not allocated_schedule.get(full_pos_str):
            time_slot, position_name = full_pos_str.split(" - ")
            
            dynamic_exclusions_for_this_slot = collections.defaultd
