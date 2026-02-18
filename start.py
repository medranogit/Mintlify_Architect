import os
import json
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from datetime import datetime

# Filtro de arquivos para focar em código e scripts técnicos
BLACKLIST_EXT = {'.exe', '.pdb', '.dll', '.bin', '.obj', '.pyc', '.cache', '.o', '.zip', '.png', '.jpg'}

def selecionar_pasta_raiz():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    caminho = filedialog.askdirectory(title="Selecione a pasta do Servidor")
    root.destroy()
    return caminho

def get_next_import_folder():
    i = 1
    while os.path.exists(f"Import_{i}"):
        i += 1
    return Path(f"Import_{i}")

def exibir_menu_selecao(pasta_raiz):
    print(f"\n📂 Analisando pastas em: {pasta_raiz}")
    pastas = [f for f in os.listdir(pasta_raiz) if os.path.isdir(os.path.join(pasta_raiz, f)) and not f.startswith('.')]
    print("[0] >>> GLOBAL (Arquivos soltos na raiz) <<<")
    for i, pasta in enumerate(pastas, 1):
        print(f"[{i}] {pasta}")
    escolhas = input("\nSelecione (ex: 0,12,28) ou 'all': ")
    if escolhas.lower() == 'all': return ["."] + pastas
    try:
        indices = [int(x.strip()) for x in escolhas.split(',')]
        return ["." if i == 0 else pastas[i-1] for i in indices if 0 <= i <= len(pastas)]
    except: return []

# --- PARSER DO DESIGN DE NAVEGAÇÃO ---
def ler_doc_design_v20():
    design_path = Path("doc_design.txt")
    if not design_path.exists():
        return ["[projeto_pastas]", "Project", []]
    
    estrutura = []
    nome_projeto = "Project"
    current_group = None
    current_page = None
    dentro_projeto_pastas = False
    
    with open(design_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith("[") and line.endswith("]"):
                tag = line[1:-1]
                if tag == "projeto_pastas":
                    dentro_projeto_pastas = True
                    estrutura.append("[projeto_pastas]")
                    current_group = None
                else:
                    dentro_projeto_pastas = False
                    current_group = {"type": "group", "name": tag, "pages": []}
                    estrutura.append(current_group)
                continue
            if line.startswith("@"):
                if dentro_projeto_pastas: nome_projeto = line[1:].strip()
                elif current_group:
                    current_page = {"sidebar": line[1:].strip(), "title": "", "desc": "", "content": ""}
                    current_group["pages"].append(current_page)
                continue
            if ":" in line and current_page and not dentro_projeto_pastas:
                key, value = line.split(":", 1)
                if key.strip().lower() == "title": current_page["title"] = value.strip()
                elif key.strip().lower() == "desc": current_page["desc"] = value.strip()
                elif key.strip().lower() == "content": current_page["content"] = value.strip()
    return estrutura, nome_projeto

# --- NOVO: PARSER DO LAYOUT PADRÃO DOS MDX DO PROJETO ---
def ler_layout_mdx_project():
    path = Path("doc_mdx_design_project.txt")
    if not path.exists():
        # Layout padrão básico caso o arquivo não exista
        return "---\ntitle: '{title}'\ndescription: '{desc}'\n---\n\n![Hero]({img})\n\n{content}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def build_nav_tree(projeto_data, nome_projeto):
    tree = {}
    for item in projeto_data:
        sub_path = os.path.dirname(item['caminho_relativo'])
        prefixo = f"{nome_projeto}/{sub_path}" if sub_path and sub_path != "." else nome_projeto
        full_route = f"{prefixo}/{item['nome_arquivo_mdx']}".replace("//", "/")
        path_parts = sub_path.split('/') if sub_path and sub_path != "." else []
        current = tree
        for part in path_parts:
            clean_p = part.replace("_", " ").capitalize()
            if clean_p not in current or not isinstance(current[clean_p], dict):
                current[clean_p] = {"_is_group": True, "children": {}}
            current = current[clean_p]["children"]
        current[item['nome_exibicao']] = full_route

    def format_node(node):
        res = []
        for key in sorted(node.keys()):
            val = node[key]
            if isinstance(val, dict) and val.get("_is_group"):
                res.append({"group": key, "pages": format_node(val["children"])})
            else: res.append(val)
        return res
    return format_node(tree)

def construir_projeto_mint(nome_projeto, dados, estrutura_design):
    import_path = get_next_import_folder()
    projeto_path = import_path / nome_projeto
    import_path.mkdir(parents=True)
    projeto_path.mkdir(parents=True)

    # Carrega o layout customizado para os arquivos do projeto
    template_mdx = ler_layout_mdx_project()

    print(f"\n🚀 Gerando Import: {import_path.name}...")

    navigation_groups = []
    for item in estrutura_design:
        if item == "[projeto_pastas]":
            nav_tree = build_nav_tree(dados, nome_projeto)
            navigation_groups.append({"group": nome_projeto, "pages": nav_tree})
        elif isinstance(item, dict):
            group_name = item["name"]
            routes = []
            for pg in item["pages"]:
                safe_name = pg["sidebar"].lower().replace(" ", "_")
                mdx_file = import_path / "introducao.mdx" if "introdu" in safe_name else import_path / group_name.lower().replace(" ", "_") / f"{safe_name}.mdx"
                mdx_file.parent.mkdir(exist_ok=True)
                route = "introducao" if "introdu" in safe_name else f"{group_name.lower().replace(' ', '_')}/{safe_name}"
                routes.append(route)
                # Páginas estáticas usam o layout do doc_design.txt
                with open(mdx_file, "w", encoding="utf-8") as f:
                    f.write(f'---\ntitle: "{pg["title"]}"\ndescription: "{pg["desc"]}"\n---\n\n{pg["content"]}')
            navigation_groups.append({"group": group_name, "pages": routes})

    # Criar MDX Técnicos usando o TEMPLATE CUSTOMIZADO
    for arquivo in dados:
        sub_dir = projeto_path / os.path.dirname(arquivo['caminho_relativo'])
        sub_dir.mkdir(parents=True, exist_ok=True)
        
        # Escapa aspas duplas caso existam no nome para não quebrar o YAML
        titulo_seguro = arquivo["nome_exibicao"].replace('"', '\\"')
        desc_segura = f"Documentação técnica de {titulo_seguro}".replace('"', '\\"')
        
        # Preenche o template
        mdx_final = template_mdx.format(
            title=titulo_seguro,
            desc=desc_segura,
            img="/images/hero-dark.png",
            content=arquivo['caminho_relativo']
        )
        
        with open(sub_dir / f"{arquivo['nome_arquivo_mdx']}.mdx", "w", encoding="utf-8") as f:
            f.write(mdx_final)

    # docs.json
    layout_path = Path("layout_mint.json")
    layout_data = json.load(open(layout_path, "r", encoding="utf-8")) if layout_path.exists() else {}
    layout_data["navigation"] = {"groups": navigation_groups}
    layout_data["name"] = nome_projeto
    with open(import_path / "docs.json", "w", encoding="utf-8") as f:
        json.dump(layout_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Finalizado! Layout aplicado aos MDX do projeto.")

def main():
    print("\n" + "="*45 + "\n MINTLIFY ARCHITECT V20.0 (LAYOUT ENGINE) \n" + "="*45)
    estrutura, nome_projeto = ler_doc_design_v20()
    raiz = selecionar_pasta_raiz()
    if raiz and (selec := exibir_menu_selecao(raiz)):
        dados = []
        for item in selec:
            origem = os.path.join(raiz, item)
            walk_gen = os.walk(origem) if item != "." else [(raiz, [], os.listdir(raiz))]
            for r, d, files in walk_gen:
                if item == "." and r != raiz: continue
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if f.startswith('.') or ext in BLACKLIST_EXT: continue
                    rel = os.path.relpath(os.path.join(r, f), raiz).replace("\\", "/")
                    dados.append({
                        "nome_exibicao": f, 
                        "nome_arquivo_mdx": f.replace(".", "_"), 
                        "caminho_relativo": rel,
                        "tamanho": round(os.path.getsize(os.path.join(r, f)) / 1024, 2),
                        "data": datetime.fromtimestamp(os.path.getmtime(os.path.join(r, f))).strftime('%d/%m/%Y %H:%M')
                    })
        construir_projeto_mint(nome_projeto, dados, estrutura)

if __name__ == "__main__":
    main()