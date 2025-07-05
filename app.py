import streamlit as st
import random
import collections
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
import io # Para manipular arquivos em memória
import pandas as pd # Para exibir DataFrames no Streamlit

# --- Configuration Data ---
# Core positions for Before/After Dinner
CORE_POSITIONS = [
    "Recirculação", "Pesado", "Auditoria 1", "Auditoria 2", "Azul",
    "Shuttle 1", "Shuttle 2", "Shuttle 3", "Shuttle 4", "GAP",
    "Carregamento"
]

# Mapeamento de posições conceituais para aplicar a regra "não pode estar em conceituais iguais"
CONCEPTUAL_POSITION_GROUPS = {
    "Shuttle": ["Shuttle 1", "Shuttle 2", "Shuttle 3", "Shuttle 4"],
    "Auditoria": ["Auditoria 1", "Auditoria 2"],
    "Recirculação": ["Recirculação"],
    "Pesado": ["Pesado"],
    "Azul": ["Azul"],
    "GAP": ["GAP"],
    "Carregamento": ["Carregamento"]
}

_INVERTED_CONCEPTUAL_GROUPS = {}
for group, positions in CONCEPTUAL_POSITION_GROUPS.items():
    for pos in positions:
        _INVERTED_CONCEPTUAL_GROUPS[pos] = group

ACTIVATED_FUNCTIONS = [
    "Hatae - tirar pacote", "Triagem 1", "Triagem 2", "Triagem 3",
    "Triagem 4", "Bipando Hatae", "Curva - Tirar Hatae"
]

ALLOWED_IN_AZUL = ["rinalanc", "leonarsd", "horaroge", "silvnpau", "sousthib"]

EXCLUSIONS = {
    "rinalanc": {
        "GeneralCeia": ["Shuttle 1", "Shuttle 2", "Shuttle 3", "Shuttle 4", "Recirculação", "Pesado", "GAP"],
        "GeneralDraw": ["Shuttle 1", "Shuttle 2", "Shuttle 3", "Shuttle 4",
                        "Recirculação", "Pesado", "GAP", "Hatae - tirar pacote", "Triagem 1", "Triagem 2", "Triagem 3", "Triagem 4",
                        "Bipando Hatae", "Curva - Tirar Hatae"]
    },
    "leonarsd": {
        "GeneralCeia": ["Shuttle 1", "Shuttle 2", "Shuttle 3", "Shuttle 4", "Recirculação", "Pesado", "GAP"],
        "GeneralDraw": ["Shuttle 1", "Shuttle 2", "Shuttle 3", "Shuttle 4",
                        "Recirculação", "Pesado", "GAP", "Hatae - tirar pacote", "Triagem 1", "Triagem 2", "Triagem 3", "Triagem 4",
                        "Bipando Hatae", "Curva - Tirar Hatae"]
    },
    "horaroge": {
        "GeneralCeia": ["Pesado"],
        "GeneralDraw": ["Pesado"]
    },
    "silvnpau": {
        # Sem exclusões específicas.
    },
    "sousthib": {
        # Sem exclusões específicas.
    },
    "ferrlucq": {
        "GeneralCeia": ["Azul", "Carregamento"],
        "GeneralDraw": ["Azul", "Carregamento"]
    },
    "ksilsilv": {
        "GeneralCeia": ["Azul", "Carregamento"],
        "GeneralDraw": ["Azul", "Carregamento"]
    },
    "wessouzf": {
        "GeneralCeia": ["Azul", "Carregamento"],
        "GeneralDraw": ["Azul", "Carregamento"]
    },
    "piluanaq": {
        # Sem exclusões específicas.
    },
    "pretojon": { # Adicionado para garantir que esteja completo
        "GeneralCeia": [], # Adicione exclusões se houver
        "GeneralDraw": []  # Adicione exclusões se houver
    },
    "EVAWWELI": { # Adicionado
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "rabsouza": { # Adicionado
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "lucenama": { # Adicionado
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "pedrour": { # Adicionado
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "ferrlnat": { # Adicionado
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "doubsant": { # Adicionado
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "vinichda": { # Adicionado
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "hjosesil": { # Adicionado
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "tmarcoso": { # Adicionado
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "luizsanp": { # Adicionado
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "nasckluc": { # Adicionado
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "salucasi": { # Adicionado
        "GeneralCeia": [],
        "GeneralDraw": []
    },
    "mlucneri": { # Adicionado
        "GeneralCeia": [],
        "GeneralDraw": []
    }
}

INCREASED_PROBABILITY = {
    "rinalanc": {
        "GeneralCeia": { "Azul": 4, "Auditoria 1": 3, "Auditoria 2": 3, "Carregamento": 3 },
        "GeneralDraw": { "Azul": 4, "Auditoria 1": 3, "Auditoria 2": 3, "Carregamento": 4 }
    },
    "leonarsd": {
        "GeneralCeia": { "Azul": 4, "Auditoria 1": 3, "Auditoria 2": 3, "Carregamento": 3 },
        "GeneralDraw": { "Azul": 4, "Auditoria 1": 3, "Auditoria 2": 3, "Carregamento": 4 }
    },
    "horaroge": {
        "GeneralCeia": { "Azul": 1, "Carregamento": 2, "Auditoria 1": 2, "Auditoria 2": 2, "Recirculação": 1, "GAP": 1, "Shuttle 1": 1, "Shuttle 2": 1, "Shuttle 3": 1, "Shuttle 4": 1 },
        "GeneralDraw": { "Azul": 4, "Carregamento": 2, "Hatae - tirar pacote": 1, "Triagem 1": 1, "Triagem 2": 1, "Triagem 3": 1, "Triagem 4": 1, "Bipando Hatae": 1, "Curva - Tirar Hatae": 1 }
    },
    "silvnpau": {
        "GeneralCeia": { "Azul": 1, "Carregamento": 2, "Recirculação": 1, "Pesado": 1, "Auditoria 1": 1, "Auditoria 2": 1, "Shuttle 1": 1, "Shuttle 2": 1, "Shuttle 3": 1, "Shuttle 4": 1, "GAP": 1 },
        "GeneralDraw": { "Azul": 4, "Carregamento": 2, "Hatae - tirar pacote": 1, "Triagem 1": 1, "Triagem 2": 1, "Triagem 3": 1, "Triagem 4": 1, "Bipando Hatae": 1, "Curva - Tirar Hatae": 1 }
    },
    "sousthib": {
        "GeneralCeia": { "Azul": 1, "Carregamento": 2, "Pesado": 2, "Auditoria 1": 1, "Auditoria 2": 1, "Recirculação": 1, "GAP": 1, "Shuttle 1": 1, "Shuttle 2": 1, "Shuttle 3": 1, "Shuttle 4": 1 },
        "GeneralDraw": { "Azul": 4, "Carregamento": 2, "Pesado": 2, "Hatae - tirar pacote": 1, "Triagem 1": 1, "Triagem 2": 1, "Triagem 3": 1, "Triagem 4": 1, "Bipando Hatae": 1, "Curva - Tirar Hatae": 1 }
    },
    "ferrlucq": {
        "GeneralCeia": {
            "GAP": 2, "Shuttle 1": 2, "Shuttle 2": 2, "Shuttle 3": 2, "Shuttle 4": 2,
            "Recirculação": 2, "Pesado": 2
        },
        "GeneralDraw": {
            "Pesado": 2, "GAP": 2, "Recirculação": 2,
            "Hatae - tirar pacote": 2, "Triagem 1": 2, "Triagem 2": 2,
            "Triagem 3": 2, "Triagem 4": 2, "Bipando Hatae": 2, "Curva - Tirar Hatae": 2,
            "Shuttle 1": 2, "Shuttle 2": 2, "Shuttle 3": 2, "Shuttle 4": 2
        }
    },
    "ksilsilv": {
        "GeneralCeia": {
            "GAP": 2, "Shuttle 1": 2, "Shuttle 2": 2, "Shuttle 3": 2, "Shuttle 4": 2,
            "Recirculação": 2, "Pesado": 2
        },
        "GeneralDraw": {
            "Pesado": 2, "GAP": 2, "Recirculação": 2,
            "Hatae - tirar pacote": 2, "Triagem 1": 2, "Triagem 2": 2,
            "Triagem 3": 2, "Triagem 4": 2, "Bipando Hatae": 2, "Curva - Tirar Hatae": 2,
            "Shuttle 1": 2, "Shuttle 2": 2, "Shuttle 3": 2, "Shuttle 4": 2
        }
    },
    "pretojon": {
        "GeneralDraw": { "Azul": 3, "Auditoria 1": 2, "Auditoria 2": 2, "Carregamento": 2 }
    },
    "wessouzf": {
        "GeneralCeia": { "Recirculação": 2, "GAP": 3, "Auditoria 1": 1, "Auditoria 2": 1, "Shuttle 1": 1, "Shuttle 2": 1, "Shuttle 3": 1, "Shuttle 4": 1, "Pesado": 1 },
        "GeneralDraw": { "Recirculação": 2, "GAP": 3, "Hatae - tirar pacote": 1, "Triagem 1": 1, "Triagem 2": 1, "Triagem 3": 1, "Triagem 4": 1, "Bipando Hatae": 1, "Curva - Tirar Hatae": 1, "Auditoria 1": 1, "Auditoria 2": 1, "Shuttle 1": 1, "Shuttle 2": 1, "Shuttle 3": 1, "Shuttle 4": 1, "Pesado": 1 }
    },
    "piluanaq": {
        "GeneralCeia": { "Bipando Hatae": 2, "Recirculação": 2, "Auditoria 1": 2, "Auditoria 2": 2, "GAP": 2, "Pesado": 1, "Shuttle 1": 1, "Shuttle 2": 1, "Shuttle 3": 1, "Shuttle 4": 1, "Carregamento": 1 },
        "GeneralDraw": { "Bipando Hatae": 2, "Recirculação": 2, "Auditoria 1": 2, "Auditoria 2": 2, "GAP": 2, "Pesado": 1, "Shuttle 1": 1, "Shuttle 2": 1, "Shuttle 3": 1, "Shuttle 4": 1, "Carregamento": 1, "Hatae - tirar pacote": 1, "Triagem 1": 1, "Triagem 2": 1, "Triagem 3": 1, "Triagem 4": 1, "Curva - Tirar Hatae": 1 }
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

        # 1. IMMEDIATE EXCLUSIONS (HIGHEST PRIORITY)

        # Check general exclusion for Azul if associate is not in ALLOWED_IN_AZUL
        if position_name == "Azul" and assoc not in ALLOWED_IN_AZUL:
            is_eligible = False
        
        # Check explicit exclusions from the EXCLUSIONS dictionary
        if is_eligible and assoc in exclusions:
            assoc_exclusions = exclusions[assoc]
            
            # Check if current position_name is in the specific time_slot_context's exclusions (e.g., "AntesCeia" if that's a direct key)
            if time_slot_context in assoc_exclusions and position_name in assoc_exclusions[time_slot_context]:
                is_eligible = False
            # If not excluded by specific context, check if it's in the general context (e.g., GeneralCeia/GeneralDraw)
            elif is_eligible: # Only check if not already excluded by a more specific rule
                # Apply GeneralCeia rules for AntesCeia and DepoisCeia contexts
                if "GeneralCeia" in assoc_exclusions and \
                   (time_slot_context.startswith("AntesCeia") or time_slot_context.startswith("DepoisCeia")) and \
                   position_name in assoc_exclusions["GeneralCeia"]:
                     is_eligible = False
                # Apply GeneralDraw rules for GeneralDraw context
                elif "GeneralDraw" in assoc_exclusions and \
                     time_slot_context == "GeneralDraw" and \
                     position_name in assoc_exclusions["GeneralDraw"]:
                     is_eligible = False

        # Apply additional dynamic exclusions (e.g., based on prior allocations in the *same* shift phase)
        if is_eligible and additional_exclusions_for_assoc and assoc in additional_exclusions_for_assoc:
            if position_name in additional_exclusions_for_assoc[assoc]:
                is_eligible = False

        # If after ALL exclusions, the associate is still eligible, then apply weights
        if is_eligible:
            # Apply probability weights
            if assoc in probabilities:
                assoc_probabilities = probabilities[assoc]
                # Check specific time slot probability
                if time_slot_context in assoc_probabilities and position_name in assoc_probabilities[time_slot_context]:
                    current_weight *= assoc_probabilities[time_slot_context][position_name]
                # Check general context probability (GeneralCeia/GeneralDraw)
                elif "GeneralCeia" in assoc_probabilities and \
                     (time_slot_context.startswith("AntesCeia") or time_slot_context.startswith("DepoisCeia")) and \
                     position_name in assoc_probabilities["GeneralCeia"]:
                    current_weight *= assoc_probabilities["GeneralCeia"][position_name]
                elif "GeneralDraw" in assoc_probabilities and \
                     time_slot_context == "GeneralDraw" and \
                     position_name in assoc_probabilities["GeneralDraw"]:
                    current_weight *= assoc_probabilities["GeneralDraw"][position_name]
            
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
            
            dynamic_exclusions_for_this_slot = collections.defaultdict(list)
            
            for assoc_to_consider in associates_eligible_for_depois_ceia:
                if assoc_to_consider in antes_ceia_allocations_info:
                    antes_ceia_info = antes_ceia_allocations_info[assoc_to_consider]
                    
                    dynamic_exclusions_for_this_slot[assoc_to_consider].append(antes_ceia_info["exact_position"])
                    
                    conceptual_group_name = antes_ceia_info["conceptual_group"]
                    if conceptual_group_name in CONCEPTUAL_POSITION_GROUPS:
                        for pos_in_group in CONCEPTUAL_POSITION_GROUPS[conceptual_group_name]:
                            if pos_in_group not in dynamic_exclusions_for_this_slot[assoc_to_consider]:
                                dynamic_exclusions_for_this_slot[assoc_to_consider].append(pos_in_group)

            chosen_associate = choose_associate_with_rules(
                associates_eligible_for_depois_ceia, position_name, time_slot, exclusions, increased_probability,
                additional_exclusions_for_assoc=dynamic_exclusions_for_this_slot
            )
            
            if chosen_associate:
                allocated_schedule[full_pos_str] = chosen_associate
                associate_ceia_slots_count[chosen_associate] += 1
                associates_eligible_for_depois_ceia.remove(chosen_associate)
            else:
                allocated_schedule[full_pos_str] = "(Vazio/Nenhum Associado Elegível)"
    
    unallocated_associates_for_next_phase = []
    for assoc in associates:
        target_slots = 2 if assoc in core_associates_for_dinner else 1
        if associate_ceia_slots_count[assoc] < target_slots:
            unallocated_associates_for_next_phase.append(assoc)

    return allocated_schedule, unallocated_associates_for_next_phase

# --- Drawing Function (Including Activated Functions) - ADAPTADA PARA WEB ---
def draw_activated_functions(associates, exclusions, increased_probability, activate_extras_flag, num_draws_input):
    activate_extras = activate_extras_flag
    num_draws = num_draws_input

    if not activate_extras or num_draws <= 0:
        return {}

    drawn_assignments = {} 
    available_associates_for_draw = list(associates) 
    conceptual_role_pool_for_draw = list(ACTIVATED_FUNCTIONS) 
    random.shuffle(conceptual_role_pool_for_draw) 

    for i in range(num_draws):
        chosen_associate = None
        chosen_conceptual_role = "(Não definido)"

        if conceptual_role_pool_for_draw:
            chosen_conceptual_role = conceptual_role_pool_for_draw.pop(0) 
        else:
            chosen_conceptual_role = f"Posição Geral Extra {i+1}" 
        
        chosen_associate = choose_associate_with_rules(
            available_associates_for_draw, chosen_conceptual_role, "GeneralDraw", exclusions, increased_probability
        )

        if chosen_associate:
            drawn_assignments[f"Sorteio Posição {i+1} ({chosen_conceptual_role})"] = chosen_associate
            available_associates_for_draw.remove(chosen_associate)
        else:
            drawn_assignments[f"Sorteio Posição {i+1} ({chosen_conceptual_role})"] = "(Vazio/Nenhum Associado Elegível)"

        if not available_associates_for_draw and i < num_draws - 1:
            for j in range(i + 1, num_draws):
                if conceptual_role_pool_for_draw:
                    remaining_role = conceptual_role_pool_for_draw.pop(0)
                    drawn_assignments[f"Sorteio Posição {j+1} ({remaining_role})"] = "(Vazio)"
                else:
                    drawn_assignments[f"Sorteio Posição {j+1} (Vazio)"] = "(Vazio)"
            break
    return drawn_assignments

# --- Função para gerar o Excel em memória (ADAPTADA PARA WEB) ---
def generate_excel_in_memory(allocated_schedule, drawn_assignments, all_unallocated_associates, model_workbook_path="modelo_escala.xlsx"):
    try:
        # Carrega o modelo de escala do repositório GitHub (que o Streamlit monta como sistema de arquivos)
        workbook = load_workbook(model_workbook_path)
    except FileNotFoundError:
        # Se o modelo não for encontrado, crie um novo workbook simples
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Escala de Alocação"
        # Adicione alguns cabeçalhos básicos para não ficar vazio
        sheet['A1'] = "Posição"
        sheet['B1'] = "Antes Ceia"
        sheet['C1'] = "Depois Ceia"
        sheet['A17'] = "Funções Extras Sorteadas:"
        sheet['F1'] = "Associados Não Alocados/Sorteados:"
    
    sheet = workbook.active
    
    # Mapeamento de células do Excel para as posições de ceia
    ceia_mapping = {
        'Recirculação': {'AntesCeia': 'B2', 'DepoisCeia': 'C2'},
        'Pesado': {'AntesCeia': 'B3', 'DepoisCeia': 'C3'},
        'Auditoria 1': {'AntesCeia': 'B4', 'DepoisCeia': 'C4'},
        'Auditoria 2': {'AntesCeia': 'B5', 'DepoisCeia': 'C5'},
        'Azul': {'AntesCeia': 'B6', 'DepoisCeia': 'C6'},
        'Shuttle 1': {'AntesCeia': 'B8', 'DepoisCeia': 'C8'},
        'Shuttle 2': {'AntesCeia': 'B9', 'DepoisCeia': 'C9'},
        'Shuttle 3': {'AntesCeia': 'B10', 'DepoisCeia': 'C10'},
        'Shuttle 4': {'AntesCeia': 'B11', 'DepoisCeia': 'C11'},
        'GAP': {'AntesCeia': 'B12', 'DepoisCeia': 'C12'},
        'Carregamento': {'AntesCeia': 'B13', 'DepoisCeia': 'C13'},
    }

    # Limpar células de resultados anteriores (se houver)
    for row_num in range(2, 14): # Linhas das posições de ceia
        sheet[f'B{row_num}'] = ""
        sheet[f'C{row_num}'] = ""
    
    funcoes_ativas_start_row = 18
    for row_num in range(funcoes_ativas_start_row, funcoes_ativas_start_row + 20): # Limpar funções extras
        sheet[f'C{row_num}'] = "" # Coluna onde o associado é escrito

    unallocated_text_col = 'F'
    unallocated_text_row = 2
    for row_num in range(unallocated_text_row, unallocated_text_row + 30): # Limpar não alocados
        sheet[f'{unallocated_text_col}{row_num}'] = ""
    
    # Escrever alocações de ceia
    for full_pos_str, associate in allocated_schedule.items():
        time_slot, position_name = full_pos_str.split(" - ")
        if position_name in ceia_mapping and time_slot in ceia_mapping[position_name]:
            cell = ceia_mapping[position_name][time_slot]
            sheet[cell] = associate

    # Escrever atribuições do sorteio
    current_active_row = funcoes_ativas_start_row
    sorted_drawn_assignments_excel = sorted(drawn_assignments.items(), key=lambda item: int(item[0].split(' ')[2]))
    for full_pos_key, associate in sorted_drawn_assignments_excel:
        # sheet[f'B{current_active_row}'] = full_pos_key # Coluna para o nome da função (opcional, se o modelo tiver)
        if not associate.startswith('('): # Não escreve "(Vazio)"
            sheet[f'C{current_active_row}'] = associate
        current_active_row += 1

    # Escrever associados não alocados/sorteados
    current_unallocated_row = unallocated_text_row
    for assoc in all_unallocated_associates:
        sheet[f'{unallocated_text_col}{current_unallocated_row}'] = f"- {assoc}"
        current_unallocated_row += 1

    # Salva o workbook em um buffer de bytes
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0) # Retorna o ponteiro para o início do buffer
    return buffer.getvalue() # Retorna os bytes do arquivo Excel

# --- Streamlit App Interface ---
st.set_page_config(page_title="Alocador de Escalas", page_icon="📊", layout="centered")

st.title("📊 Alocador Automático de Escalas e Sorteios")
st.markdown("Bem-vindo ao seu assistente de alocação de equipes!")
st.markdown("---")

# --- 1. Carregar Associados ---
st.header("1. Carregar Lista de Associados")
st.info("Por favor, carregue um arquivo `.txt` contendo os nomes dos associados, um por linha.")
uploaded_associates_file = st.file_uploader("Arraste ou clique para carregar 'associados.txt'", type="txt", key="associates_uploader")

associates = []
if uploaded_associates_file is not None:
    try:
        raw_associates = [line.strip() for line in uploaded_associates_file.getvalue().decode("utf-8").splitlines() if line.strip()]
        # Remover duplicatas mantendo a ordem original
        seen = set()
        associates = [x for x in raw_associates if not (x in seen or seen.add(x))]
        
        if associates:
            st.success(f"Arquivo 'associados.txt' carregado com sucesso! ({len(associates)} associados)")
            st.write("Associados carregados:", associates)
            st.session_state['initial_associates_set'] = set(associates) # Salva para controle final
        else:
            st.warning("O arquivo 'associados.txt' está vazio ou não contém nomes válidos.")
            st.session_state['initial_associates_set'] = set()
    except Exception as e:
        st.error(f"Erro ao ler 'associados.txt': {e}. Verifique se o formato está correto.")
        st.session_state['initial_associates_set'] = set()
else:
    st.session_state['initial_associates_set'] = set()


st.markdown("---")

# --- 2. Executar Alocação de Ceia ---
st.header("2. Alocação de Escala de Ceia")

if st.button("🚀 Iniciar Alocação de Ceia", disabled=not associates):
    if associates:
        with st.spinner("Alocando posições de ceia..."):
            allocated_schedule, unallocated_from_ceia_for_draw = allocate_dinner_shifts(
                list(associates), EXCLUSIONS, INCREASED_PROBABILITY, CORE_ASSOCIATES_FOR_DINNER
            )
            st.session_state['allocated_schedule'] = allocated_schedule
            st.session_state['unallocated_for_draw'] = unallocated_from_ceia_for_draw

            st.subheader("✅ Escala da Ceia Gerada:")
            ceia_data = []
            
            # Ordena a exibição para o usuário
            def sort_key(item_tuple): # CORREÇÃO AQUI: Recebe a tupla (chave, valor)
                item_key = item_tuple[0] # Pega apenas a chave da tupla
                time_slot_part, pos_name_part = item_key.split(" - ")
                time_slot_order = 0 if time_slot_part == "AntesCeia" else 1
                try:
                    pos_order = CORE_POSITIONS.index(pos_name_part)
                except ValueError:
                    pos_order = len(CORE_POSITIONS) # Posições desconhecidas vão para o final
                return (time_slot_order, pos_order)

            sorted_schedule_items = sorted(allocated_schedule.items(), key=sort_key)

            for full_pos_str, assoc in sorted_schedule_items:
                ceia_data.append({"Posição na Ceia": full_pos_str.replace("AntesCeia - ", "").replace("DepoisCeia - ", ""), "Associado": assoc})
            
            st.dataframe(pd.DataFrame(ceia_data))
            
            if unallocated_from_ceia_for_draw:
                st.info(f"**{len(unallocated_from_ceia_for_draw)}** associados estão elegíveis para o sorteio de funções extras.")
                st.write("Associados disponíveis para sorteio:", unallocated_from_ceia_for_draw)
            else:
                st.info("Todos os associados elegíveis foram alocados na ceia (ou não há mais elegíveis para sorteio).")
            
            st.success("Alocação de Ceia Concluída! Prossiga para o sorteio, se desejar.")
    else:
        st.warning("Por favor, carregue a lista de associados primeiro.")

st.markdown("---")

# --- 3. Sorteio de Funções Extras ---
st.header("3. Sorteio de Funções Extras")

unallocated_for_draw = st.session_state.get('unallocated_for_draw', [])
max_draws = len(ACTIVATED_FUNCTIONS) # Número máximo de funções ativadas
max_associates_for_draw = len(unallocated_for_draw)

if not unallocated_for_draw:
    st.warning("Nenhum associado disponível para sorteio de funções extras. Execute a alocação de ceia primeiro.")
else:
    activate_extras_option = st.radio(
        "Deseja ativar as funções extras?",
        ("Sim", "Não"), index=1, key="activate_extras_radio"
    )
    
    num_draws = 0
    if activate_extras_option == "Sim":
        st.info(f"Atualmente, há {max_associates_for_draw} associados disponíveis e {max_draws} funções extras possíveis.")
        num_draws = st.number_input(
            f"Quantas funções extras deseja sortear? (Máximo: {min(max_draws, max_associates_for_draw)})",
            min_value=0, max_value=min(max_draws, max_associates_for_draw), value=min(max_draws, max_associates_for_draw), key="num_draws_input"
        )

    if st.button("🎲 Executar Sorteio de Funções Extras", disabled=(activate_extras_option == "Sim" and num_draws == 0) or not unallocated_for_draw, key="draw_button"):
        if activate_extras_option == "Sim" and num_draws > 0:
            with st.spinner("Executando sorteio de funções..."):
                drawn_assignments = draw_activated_functions(
                    list(unallocated_for_draw), # Passa uma cópia para a função
                    EXCLUSIONS, INCREASED_PROBABILITY,
                    True, # activate_extras_flag
                    num_draws # num_draws_input
                )
                st.session_state['drawn_assignments'] = drawn_assignments

                st.subheader("✅ Atribuições do Sorteio Finalizadas:")
                drawn_data = []
                for pos, assoc in sorted(drawn_assignments.items()):
                    drawn_data.append({"Posição Sorteada": pos, "Associado": assoc})
                st.dataframe(pd.DataFrame(drawn_data))
                st.success("Sorteio Concluído!")
        elif activate_extras_option == "Não":
            st.info("Sorteio de funções extras desativado.")
            st.session_state['drawn_assignments'] = {} # Garante que está vazio se não sorteou
        else:
            st.warning("Número de sorteios deve ser maior que zero se ativado.")

st.markdown("---")

# --- 4. Baixar Escala Final ---
st.header("4. Baixar Escala Completa em Excel")

allocated_schedule = st.session_state.get('allocated_schedule', {})
drawn_assignments = st.session_state.get('drawn_assignments', {})
initial_associates_set = st.session_state.get('initial_associates_set', set())

if not allocated_schedule:
    st.warning("Por favor, execute a alocação de ceia primeiro para gerar o Excel.")
else:
    if st.button("💾 Gerar e Baixar Escala Completa em Excel", key="download_excel_button"):
        with st.spinner("Gerando arquivo Excel..."):
            # Obter todos os associados alocados/sorteados para a lista final de não alocados
            final_allocated_associates_set = set()
            for assoc in allocated_schedule.values():
                if not assoc.startswith('('):
                    final_allocated_associates_set.add(assoc)
            for assoc in drawn_assignments.values():
                if not assoc.startswith('('):
                    final_allocated_associates_set.add(assoc)
            
            all_unallocated_associates_overall = list(initial_associates_set - final_allocated_associates_set)
            all_unallocated_associates_overall.sort() # Para manter a ordem

            try:
                excel_bytes = generate_excel_in_memory(
                    allocated_schedule, 
                    drawn_assignments, 
                    all_unallocated_associates_overall,
                    "modelo_escala.xlsx" # Nome do arquivo do modelo que deve estar no GitHub
                )
                
                st.download_button(
                    label="Clique para Baixar 'escala_da_equipe.xlsx'",
                    data=excel_bytes,
                    file_name="escala_da_equipe.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.success("Arquivo Excel gerado com sucesso!")

                if all_unallocated_associates_overall:
                    st.subheader("Associados Restantes (Não Alocados/Sorteados em Nenhuma Posição):")
                    for assoc in all_unallocated_associates_overall:
                        st.write(f"- {assoc}")
                else:
                    st.info("🎉 Todos os associados foram alocados/sorteados para alguma posição!")

            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar o arquivo Excel: {e}")
                st.warning("Verifique se o 'modelo_escala.xlsx' está no formato correto e na mesma pasta do 'app.py' no seu repositório GitHub.")

st.markdown("---")

# --- Rodapé ---
st.markdown("Esta aplicação foi desenvolvida por **Rinalanc/Github**.")
st.markdown("Data: 30/06/2025")
