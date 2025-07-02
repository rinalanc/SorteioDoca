import streamlit as st
import pandas as pd
from openpyxl import load_workbook, Workbook # Ainda necessário para manipular Excel
import io # Para gerar o Excel em memória
# Importe suas funções de alocação de outro arquivo se preferir:
# from your_logic_module import allocate_dinner_shifts, draw_activated_functions, EXCLUSIONS, INCREASED_PROBABILITY, CORE_ASSOCIATES_FOR_DINNER, CONCEPTUAL_POSITION_GROUPS

# Ou inclua todas as suas funções e constantes no mesmo app.py
# (coloque aqui todo o código das suas funções e constantes como CORE_POSITIONS, EXCLUSIONS, etc.)
# ... (COLE SEU CÓDIGO AQUI) ...

# Título da Aplicação
st.title("📊 Alocador Automático de Escalas e Sorteios")
st.markdown("Bem-vindo ao seu assistente de alocação de equipes!")

# --- Carregar associados.txt ---
st.header("1. Carregar Associados")
uploaded_associates_file = st.file_uploader("Arraste ou clique para carregar o arquivo 'associados.txt'", type="txt", key="associates_uploader")
associates = []
if uploaded_associates_file is not None:
    # Decodificar o arquivo e remover linhas vazias/espaços
    raw_associates = [line.strip() for line in uploaded_associates_file.getvalue().decode("utf-8").splitlines() if line.strip()]
    
    # Remover duplicatas mantendo a ordem original, se houver
    seen = set()
    associates = [x for x in raw_associates if not (x in seen or seen.add(x))]
    
    if associates:
        st.success(f"Arquivo 'associados.txt' carregado com sucesso! ({len(associates)} associados)")
        st.write("Associados carregados:", associates)
    else:
        st.warning("O arquivo 'associados.txt' está vazio ou não contém nomes válidos.")
else:
    st.info("Por favor, carregue o arquivo 'associados.txt' para iniciar.")
    # Opcional: Se quiser usar uma lista padrão para teste sem upload
    # associates = ["horaroge", "leonarsd", ...] # Comente isso em produção se exigir upload


# --- Carregar modelo_escala.xlsx (Opcional, se o modelo não for fixo) ---
# Se o modelo_escala.xlsx for um template fixo e você o incluir no repositório GitHub,
# você pode carregá-lo diretamente do disco do servidor Streamlit.
# Mas se o usuário precisar fornecer o modelo, use:
st.header("2. Carregar Modelo de Escala (Opcional, se o seu não for fixo no GitHub)")
uploaded_excel_model_file = st.file_uploader("Arraste ou clique para carregar o arquivo 'modelo_escala.xlsx'", type="xlsx", key="model_uploader")
if uploaded_excel_model_file is not None:
    # Você precisará salvar isso temporariamente ou usar BytesIO para carregar no openpyxl
    # Para simplificar, neste exemplo, vamos assumir que o modelo_escala.xlsx estará no repositório.
    st.success("Modelo de Escala carregado. (Este exemplo assume que 'modelo_escala.xlsx' está no repositório.)")
    # A Lógica real de carregar o modelo a partir do upload ficaria aqui
    # Ex: workbook_model = load_workbook(uploaded_excel_model_file)
else:
    st.info("Se você não tem o 'modelo_escala.xlsx' no repositório, carregue-o aqui.")

# --- Execução da Lógica ---
if associates: # Só mostra os botões se houver associados carregados
    st.header("3. Executar Alocação e Sorteio")

    # Botão para Alocar Escalas da Ceia
    if st.button("🚀 Iniciar Alocação de Ceia"):
        with st.spinner("Alocando posições de ceia..."):
            # A função write_to_excel precisa ser adaptada para não salvar no disco, mas gerar em memória
            # Vamos gerar o Excel final no final do processo
            
            # Use as suas funções de alocação aqui
            allocated_schedule, unallocated_from_ceia_for_draw = allocate_dinner_shifts(
                list(associates), EXCLUSIONS, INCREASED_PROBABILITY, CORE_ASSOCIATES_FOR_DINNER
            )
            st.session_state['allocated_schedule'] = allocated_schedule
            st.session_state['unallocated_for_draw'] = unallocated_from_ceia_for_draw
            st.session_state['initial_associates_set'] = set(associates)

            st.subheader("✅ Escala da Ceia Gerada:")
            # Exibir a escala da ceia de forma organizada
            ceia_data = []
            for full_pos_str, assoc in sorted(allocated_schedule.items()):
                ceia_data.append({"Posição": full_pos_str, "Associado": assoc})
            st.dataframe(pd.DataFrame(ceia_data))
            
            if unallocated_from_ceia_for_draw:
                st.info(f"**{len(unallocated_from_ceia_for_draw)}** associados elegíveis para sorteio de funções extras.")
            else:
                st.info("Todos os associados foram alocados na ceia (ou não há mais elegíveis para sorteio).")
            
            st.success("Alocação de Ceia Concluída! Prossiga para o sorteio, se desejar.")

    # Seção para sorteio (só aparece após a alocação da ceia)
    if 'allocated_schedule' in st.session_state and st.session_state['allocated_schedule'] and 'unallocated_for_draw' in st.session_state:
        st.subheader("4. Sorteio de Funções Extras")
        activate_extras_option = st.radio(
            "Deseja ativar as funções extras?",
            ("Sim", "Não"), index=1, key="activate_extras_radio"
        )
        
        num_draws = 0
        if activate_extras_option == "Sim":
            num_draws = st.number_input(
                f"Número de posições para sortear (máx: {len(st.session_state['unallocated_for_draw'])} associados disponíveis):",
                min_value=0, max_value=len(st.session_state['unallocated_for_draw']), value=min(len(ACTIVATED_FUNCTIONS), len(st.session_state['unallocated_for_draw'])), key="num_draws_input"
            )

        if st.button("🎲 Executar Sorteio de Funções Extras", key="draw_button"):
            if activate_extras_option == "Sim" and num_draws > 0:
                with st.spinner("Executando sorteio de funções..."):
                    # Temporariamente modificar a função draw_activated_functions para não pedir input
                    # ou passar os parâmetros diretamente
                    
                    # Adapte draw_activated_functions para não ter input()
                    # A lógica aqui precisaria ser cuidadosamente ajustada
                    # No seu código original, draw_activated_functions já recebe o número de sorteios se for alterada.
                    
                    # Supondo uma versão adaptada de draw_activated_functions que não pede input
                    # Ou você passa activate_extras e num_draws para ela se ela aceitar
                    drawn_assignments = draw_activated_functions_web_version(
                        list(st.session_state['unallocated_for_draw']), EXCLUSIONS, INCREASED_PROBABILITY, num_draws
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
            else:
                st.warning("Número de sorteios deve ser maior que zero se ativado.")

    # --- Gerar Excel Final ---
    if 'allocated_schedule' in st.session_state: # Verifica se a ceia foi alocada
        st.header("5. Baixar Escala Final")
        
        # Obter todos os associados alocados/sorteados
        final_allocated_associates_set = set()
        for assoc in st.session_state['allocated_schedule'].values():
            if not assoc.startswith('('):
                final_allocated_associates_set.add(assoc)
        if 'drawn_assignments' in st.session_state:
            for assoc in st.session_state['drawn_assignments'].values():
                if not assoc.startswith('('):
                    final_allocated_associates_set.add(assoc)
        
        all_unallocated_associates_overall = list(st.session_state['initial_associates_set'] - final_allocated_associates_set)

        if st.button("💾 Gerar e Baixar Escala Completa em Excel"):
            with st.spinner("Gerando arquivo Excel..."):
                # A função `write_to_excel` precisa ser adaptada para não usar um nome de arquivo fixo
                # e para retornar os bytes do workbook em memória.
                
                # Adapte sua função write_to_excel:
                # 1. Remova o argumento `output_filename` e a chamada `workbook.save(output_filename)`.
                # 2. Em vez de salvar, use `buffer = io.BytesIO()` e `workbook.save(buffer)`
                # 3. Retorne `buffer.getvalue()`
                
                # Exemplo (você precisa adaptar a sua função original):
                excel_buffer = io.BytesIO()
                # Carregar o modelo do GitHub
                try:
                    # Carrega o modelo de escala do repositório GitHub
                    # O Streamlit monta seu repositório como um sistema de arquivos.
                    workbook = load_workbook("modelo_escala.xlsx")
                except FileNotFoundError:
                    st.error("Erro: 'modelo_escala.xlsx' não encontrado no repositório. Por favor, adicione-o ao seu GitHub.")
                    st.stop()

                sheet = workbook.active
                sheet.title = "Escala de Alocação"

                # Restante da sua lógica de escrita no Excel, como no write_to_excel original
                # ... (COLE A LÓGICA DE ESCRITA NO EXCEL AQUI) ...

                # Salvar o workbook no buffer e obter os bytes
                workbook.save(excel_buffer)
                excel_bytes = excel_buffer.getvalue()

                st.download_button(
                    label="Clique para Baixar 'escala_da_equipe.xlsx'",
                    data=excel_bytes,
                    file_name="escala_da_equipe.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.success("Arquivo Excel gerado com sucesso!")
        
        if all_unallocated_associates_overall:
            st.subheader("Associados Não Alocados/Sorteados (Final):")
            for assoc in all_unallocated_associates_overall:
                st.write(f"- {assoc}")
        else:
            st.info("🎉 Todos os associados foram alocados/sorteados para alguma posição!")


# --- Rodapé ---
st.markdown("---")
st.markdown("Esta aplicação foi desenvolvida por **Rinalanc/Github**.")
st.markdown("Data: 30/06/2025")