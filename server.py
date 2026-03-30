import json
import uuid
import sqlite3
import webbrowser
import threading
import sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent

DB         = BASE_DIR.parent / "pascalina.db"
STATIC_DIR = BASE_DIR / "static"

CATS_PADRAO = {
    "receita": ["salário", "freelance", "investimento", "aluguel recebido", "dividendos", "vr / benefícios", "outro"],
    "despesa": ["moradia", "alimentação", "transporte", "saúde", "lazer", "educação", "assinaturas", "cartão", "vestuário", "outro"],
}


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS lancamentos (
            id        TEXT PRIMARY KEY,
            descricao TEXT NOT NULL,
            valor     REAL NOT NULL,
            categoria TEXT,
            data      TEXT NOT NULL,
            tipo      TEXT NOT NULL,
            natureza  TEXT DEFAULT 'variavel'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id   TEXT PRIMARY KEY,
            nome TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL
        )
    """)

    c.execute("SELECT COUNT(*) FROM categorias")
    if c.fetchone()[0] == 0:
        for tipo, nomes in CATS_PADRAO.items():
            for nome in nomes:
                c.execute(
                    "INSERT OR IGNORE INTO categorias (id, nome, tipo) VALUES (?, ?, ?)",
                    (str(uuid.uuid4()), nome, tipo)
                )

    conn.commit()
    conn.close()


def get_all():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, descricao, valor, categoria, data, tipo, natureza FROM lancamentos ORDER BY data DESC")
    rows = c.fetchall()
    conn.close()
    return [
        {"id": r[0], "descricao": r[1], "valor": r[2], "categoria": r[3],
         "data": r[4], "tipo": r[5], "natureza": r[6] or "variavel"}
        for r in rows
    ]


def insert(data):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO lancamentos (id, descricao, valor, categoria, data, tipo, natureza) VALUES (?,?,?,?,?,?,?)",
        (data["id"], data["descricao"], data["valor"], data["categoria"],
         data["data"], data["tipo"], data.get("natureza", "variavel"))
    )
    conn.commit()
    conn.close()


def delete_item(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM lancamentos WHERE id=?", (id,))
    conn.commit()
    conn.close()


def update_item(data):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        UPDATE lancamentos
        SET descricao=?, valor=?, categoria=?, data=?, tipo=?, natureza=?
        WHERE id=?
    """, (data["descricao"], data["valor"], data["categoria"],
          data["data"], data["tipo"], data.get("natureza", "variavel"), data["id"]))
    conn.commit()
    conn.close()


def get_categorias():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, nome, tipo FROM categorias ORDER BY tipo, nome")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "nome": r[1], "tipo": r[2]} for r in rows]


def criar_categoria(nome, tipo):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO categorias (id, nome, tipo) VALUES (?,?,?)",
                  (str(uuid.uuid4()), nome.strip(), tipo))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def editar_categoria(id, nome_novo, nome_antigo, tipo):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute("UPDATE lancamentos SET categoria=? WHERE categoria=?", (nome_novo.strip(), nome_antigo))
        c.execute("UPDATE categorias SET nome=?, tipo=? WHERE id=?", (nome_novo.strip(), tipo, id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def deletar_categoria(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM categorias WHERE id=?", (id,))
    conn.commit()
    conn.close()


def validar(body):
    try:
        if not isinstance(body.get("descricao"), str) or not body["descricao"]:
            return False
        if not isinstance(body.get("valor"), (int, float)):
            return False
        if body.get("tipo") not in ["receita", "despesa"]:
            return False
        if body.get("natureza") not in ["fixa", "variavel", None]:
            return False
        if not body.get("data"):
            return False
        return True
    except Exception:
        return False


class Handler(BaseHTTPRequestHandler):

    def log_message(self, *args):
        pass

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _serve_file(self, path):
        try:
            with open(path, "rb") as f:
                self.send_response(200)
                if path.suffix == ".html":
                    self.send_header("Content-Type", "text/html")
                elif path.suffix == ".css":
                    self.send_header("Content-Type", "text/css")
                elif path.suffix == ".js":
                    self.send_header("Content-Type", "application/javascript")
                self.end_headers()
                self.wfile.write(f.read())
        except Exception:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            return self._serve_file(STATIC_DIR / "index.html")
        elif path.startswith("/static/"):
            return self._serve_file(BASE_DIR / path.strip("/"))
        elif path == "/api/dados":
            return self._json(200, get_all())
        elif path == "/api/categorias":
            return self._json(200, get_categorias())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))

        if path == "/api/lancar":
            if not validar(body):
                return self._json(400, {"erro": "dados inválidos"})
            body["id"] = str(uuid.uuid4())
            body["valor"] = round(float(body["valor"]), 2)
            body.setdefault("natureza", "variavel")
            insert(body)
            return self._json(200, {"ok": True})

        elif path == "/api/delete":
            if not body.get("id"):
                return self._json(400, {"erro": "id obrigatório"})
            delete_item(body["id"])
            return self._json(200, {"ok": True})

        elif path == "/api/update":
            if not body.get("id"):
                return self._json(400, {"erro": "id obrigatório"})
            update_item(body)
            return self._json(200, {"ok": True})

        elif path == "/api/categoria/criar":
            nome = body.get("nome", "").strip()
            tipo = body.get("tipo", "")
            if not nome or tipo not in ["receita", "despesa"]:
                return self._json(400, {"erro": "dados inválidos"})
            ok = criar_categoria(nome, tipo)
            if ok:
                return self._json(200, {"ok": True})
            return self._json(409, {"erro": "categoria já existe"})

        elif path == "/api/categoria/editar":
            id_    = body.get("id", "")
            nome   = body.get("nome", "").strip()
            antigo = body.get("nome_antigo", "")
            tipo   = body.get("tipo", "")
            if not id_ or not nome:
                return self._json(400, {"erro": "dados inválidos"})
            ok = editar_categoria(id_, nome, antigo, tipo)
            if ok:
                return self._json(200, {"ok": True})
            return self._json(409, {"erro": "nome já existe"})

        elif path == "/api/categoria/deletar":
            if not body.get("id"):
                return self._json(400, {"erro": "id obrigatório"})
            deletar_categoria(body["id"])
            return self._json(200, {"ok": True})

        return self._json(404, {"erro": "rota não encontrada"})


def main():
    init_db()

    port = 5000
    server = ThreadingHTTPServer(("localhost", port), Handler)
    url = f"http://localhost:{port}"

    threading.Timer(1, lambda: webbrowser.open(url)).start()
    server.serve_forever()


if __name__ == "__main__":
    main()
