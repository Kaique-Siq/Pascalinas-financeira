# Pascalina — Finanças Pessoais

Sistema de controle financeiro pessoal com interface web, rodando localmente no seu computador. Sem cadastro, sem nuvem, sem internet — seus dados ficam só na sua máquina.

---

## Funcionalidades

- Lançamento de receitas e despesas com categoria, data e natureza (fixa ou variável)
- Dashboard com saldo, totais e gráfico dos últimos meses
- Filtros por tipo, natureza e busca por descrição
- Relatórios com resumo mensal, top categorias e evolução no tempo
- Regra 50·30·20 calculada mês a mês (necessidades · desejos · poupança)
- Metas financeiras vinculadas a categorias — todo lançamento naquela categoria acumula automaticamente na meta
- Gerenciamento completo de categorias (criar, editar, excluir)

---

## Como usar

### Opção 1 — Executável (recomendado)

1. Baixe o `Pascalina.exe` em [Releases](../../releases)
2. Coloque em qualquer pasta
3. Execute — o navegador abre automaticamente

O arquivo `pascalina.db` é criado na mesma pasta do `.exe` e guarda todos os seus dados.

### Opção 2 — Pelo código fonte

Requer Python 3.8 ou superior.

```bash
git clone https://github.com/seu-usuario/pascalina.git
cd pascalina
python server.py
```

O navegador abre automaticamente em `http://localhost:5000`.

---

## Como compilar o .exe

Com Python instalado, execute na pasta do projeto:

```bash
build.bat
```

O executável é gerado em `dist/Pascalina.exe`.

Ou manualmente:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "Pascalina" --add-data "static;static" server.py
```

---

## Estrutura do projeto

```
pascalina/
├── server.py          # servidor HTTP + API + banco de dados
├── build.bat          # script de build para Windows
├── .gitignore
└── static/
    └── index.html     # interface completa (single-file)
```

---

## Tecnologias

- **Python** — servidor HTTP nativo (`http.server`) e SQLite (`sqlite3`)
- **HTML / CSS / JavaScript** — interface single-file, sem frameworks
- **SQLite** — banco de dados local, arquivo único

---

## Licença

MIT — use, modifique e distribua à vontade.
