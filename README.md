# 🚀 Mintlify Architect v20.0

O **Mintlify Architect** é um motor de automação em Python desenvolvido para transformar estruturas massivas de servidores (como **Canary**, **OTServBR-Global** e projetos C++/Lua) em documentações técnicas de alto nível no [Mintlify](https://mintlify.com).

Esta ferramenta elimina o trabalho manual de criar centenas de arquivos `.mdx` e configurar o `docs.json` linha por linha, garantindo uma hierarquia de navegação idêntica à do seu código-fonte.

## ✨ Funcionalidades Pro

- **Auto-Nesting Progressivo**: Mapeia recursivamente todas as pastas do seu servidor, criando grupos e subgrupos de navegação automáticos no `docs.json`. [cite: 30, 31]
- **Versão por Importação**: Cada execução gera uma nova pasta numerada (Ex: `Import_1`, `Import_2`), evitando que você sobrescreva builds anteriores. [cite: 33]
- **Layout Engine (Template Customizado)**: Utilize o arquivo `doc_mdx_design_project.txt` para definir um template visual único para todas as páginas técnicas, com suporte a variáveis dinâmicas. [cite: 1, 38]
- **Filtro Inteligente de Arquivos**: Foca no código-fonte (.lua, .cpp, .h, .xml) e ignora automaticamente binários e caches (.exe, .dll, .obj). [cite: 34]
- **Sanitização de Sintaxe**: Corrige automaticamente nomes de arquivos com caracteres especiais (como apóstrofos `'`) para evitar erros fatais de frontmatter no build do Mintlify. [cite: 1]

## 📂 Arquitetura do Projeto

A ferramenta baseia-se em quatro pilares de configuração:

1.  **`mint_architect.py`**: O núcleo do sistema que processa os arquivos e gera a árvore.
2.  **`doc_design.txt`**: Define a hierarquia de grupos globais (Introdução, Compilação, etc.) e o nome do projeto via tag `@`. [cite: 57, 58]
3.  **`doc_mdx_design_project.txt`**: O template visual para os arquivos do servidor, aceitando variáveis como `{title}`, `{desc}`, `{size}` e `{date}`. [cite: 1, 109]
4.  **`layout_mint.json`**: Define o tema global do site (cores, logo, favicon, links do navbar). [cite: 55, 60]

## 🛠️ Como Montar e Usar

### 1. Requisitos
- **Python 3.10** ou superior.
- **Mintlify CLI** instalado globalmente:
  ```bash
  npm install -g mintlify
  ```

### 2. Configuração Inicial
Certifique-se de que os arquivos `.txt` e o `.json` estão na mesma pasta do script `.py`. Edite o `doc_design.txt` para definir seu nome de projeto favorito logo após o `[projeto_pastas]`.

### 3. Execução
Execute o arquiteto:
```bash
python mint_architect.py
```
- Uma janela abrirá para selecionar a pasta raiz do seu servidor.
- No terminal, escolha quais diretórios deseja documentar (índices separados por vírgula ou `all`).

### 4. Visualização Local
Navegue até a pasta gerada e inicie o preview em tempo real:
```bash
cd Import_1
mint dev
```

## 📄 Estrutura Gerada (Output)

```text
Import_1/
├── docs.json              # Configurações e Navegação Centralizada [cite: 27]
├── introducao.mdx         # Página de boas-vindas
├── images/                # Seus assets (hero-dark.png, etc.) [cite: 113]
└── SeuProjeto/            # Estrutura técnica mapeada fielmente
    └── data/
        └── scripts/
            └── arquivo_lua.mdx
```

---
Desenvolvido para desenvolvedores e entusiastas de documentação automatizada.