# Alocador Automático de Escalas e Sorteios

Bem-vindo ao **Alocador Automático de Escalas e Sorteios**!

Esta aplicação foi desenvolvida para facilitar a organização das escalas de ceia e o sorteio de funções adicionais, garantindo uma distribuição justa e eficiente das tarefas.

---

### **O que esta aplicação faz?**

Ela automatiza a alocação de pessoas para:

* **Posições Antes e Depois da Ceia:** Organiza 22 posições principais (11 antes da ceia e 11 depois da ceia) com base em regras específicas de exclusão e probabilidade para cada pessoa.
* **Sorteio de Funções Extras:** Permite sortear funções adicionais (como Hatae, Triagem, etc.) entre os associados que ainda não foram alocados ou que têm disponibilidade.

### **Como usar a aplicação?**

Para que a aplicação funcione corretamente, você precisará ter 3 arquivos na **MESMA PASTA**:

1.  **`alocador_associados.exe`** (Este programa que você está executando)
2.  **`associados.txt`** (Sua lista de pessoas)
3.  **`modelo_escala.xlsx`** (O modelo do Excel onde os resultados serão preenchidos)

**Passos para usar:**

1.  **Organize os arquivos:** Certifique-se de que os três arquivos mencionados acima estão juntos na mesma pasta.
2.  **Abra o programa:** Dê um clique duplo no arquivo `alocador_associados.exe`.
3.  **Siga as instruções na tela:** O programa irá guiar você com perguntas simples no console (tela preta) sobre a ativação das funções extras e a quantidade de sorteios.
4.  **Verifique o resultado:** Ao final, o programa irá gerar ou atualizar um arquivo chamado **`escala_da_equipe.xlsx`** na mesma pasta. Este arquivo conterá a escala de ceia e os resultados do sorteio.
5.  **Pressione Enter para sair:** Após a conclusão, pressione a tecla Enter para fechar a janela do programa.

**Importante:**

* **Não mova** os arquivos `associados.txt` e `modelo_escala.xlsx` para fora da pasta do executável, ou o programa não funcionará.
* **Mantenha o `associados.txt` atualizado** com os nomes das pessoas que participarão dos sorteios. Cada nome deve estar em uma linha separada.
* **O `modelo_escala.xlsx`** é o template que o programa usa. Ele deve conter a estrutura das posições de ceia.
* Este executável foi criado para **sistemas operacionais Windows**.

---

### **Créditos:**

Esta aplicação foi desenvolvida por **Rinalanc/Github**.
**Data:** 30/06/2025

---