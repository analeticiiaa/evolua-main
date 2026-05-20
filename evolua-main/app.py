from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from backend import SistemaEstudos

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "evolua_secret_key")

# CONFIGURAÇÃO DO EMAIL
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

sistema = SistemaEstudos()


def _json_erro(mensagem, status=400):
    return jsonify({"erro": mensagem}), status


def _json_sucesso(mensagem, **dados):
    resposta = {"sucesso": mensagem}
    resposta.update(dados)
    return jsonify(resposta)


def _validar_json():
    if not request.is_json:
        return _json_erro("Requisição deve ser JSON.")

    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return _json_erro("JSON inválido.")

    return dados


# ============================================================
# PROTEÇÃO DE ROTAS
# ============================================================
def login_obrigatorio(f):
    @wraps(f)
    def verificar(*args, **kwargs):
        if "usuario" not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return verificar


# ============================================================
# ROTAS DE TELAS
# ============================================================
@app.route("/")
def login():
    return render_template("login.html")

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/esqueci-senha")
def esqueci_senha():
    return render_template("esqueci-senha.html")

@app.route("/dashboard")
@login_obrigatorio
def dashboard():
    nome = session.get("usuario", "Usuário")
    return render_template("dashboard.html", pagina_ativa="dashboard", nome=nome)

@app.route("/tarefas")
@login_obrigatorio
def tarefas():
    nome = session.get("usuario", "Usuário")
    return render_template("tarefas.html", pagina_ativa="tarefas", nome=nome)

@app.route("/disciplinas")
@login_obrigatorio
def disciplinas():
    nome = session.get("usuario", "Usuário")
    return render_template("disciplinas.html", pagina_ativa="disciplinas", nome=nome)

@app.route("/sessoes")
@login_obrigatorio
def sessoes():
    nome = session.get("usuario", "Usuário")
    return render_template("sessoes.html", pagina_ativa="sessoes", nome=nome)

@app.route("/foco")
@login_obrigatorio
def foco():
    nome = session.get("usuario", "Usuário")
    return render_template("foco.html", pagina_ativa="foco", nome=nome)

@app.route("/relatorio")
@login_obrigatorio
def relatorio():
    nome = session.get("usuario", "Usuário")
    return render_template("relatorio.html", pagina_ativa="relatorio", nome=nome)

@app.route("/calendario")
@login_obrigatorio
def calendario():
    nome = session.get("usuario", "Usuário")
    return render_template("calendario.html", pagina_ativa="calendario", nome=nome)

@app.route("/configuracoes")
@login_obrigatorio
def configuracoes():
    nome = session.get("usuario", "Usuário")
    email = session.get("email", "")
    return render_template("configuracoes.html", pagina_ativa="configuracoes", nome=nome, email=email)


# ============================================================
# API — AUTENTICAÇÃO
# ============================================================

@app.route("/api/cadastrar", methods=["POST"])
def api_cadastrar():
    dados = _validar_json()
    if not isinstance(dados, dict):
        return dados

    nome = (dados.get("nome") or "").strip()
    email = (dados.get("email") or "").strip().lower()
    senha = dados.get("senha")

    if not nome or not email or not senha:
        return _json_erro("Nome, email e senha são obrigatórios.")

    if any(u["email"].lower() == email for u in sistema.dados["usuarios"]):
        return _json_erro("Email já cadastrado!", 400)

    senha_hash = generate_password_hash(senha)
    sistema.dados["usuarios"].append({"nome": nome, "email": email, "senha": senha_hash})
    sistema._salvar()
    return _json_sucesso("Usuário cadastrado!")


@app.route("/api/login", methods=["POST"])
def api_login():
    dados = _validar_json()
    if not isinstance(dados, dict):
        return dados

    email = (dados.get("email") or "").strip().lower()
    senha = dados.get("senha")

    if not email or not senha:
        return _json_erro("Email e senha são obrigatórios.")

    usuario = next((u for u in sistema.dados["usuarios"] if u["email"].lower() == email), None)
    if usuario and check_password_hash(usuario["senha"], senha):
        session["usuario"] = usuario["nome"]
        session["email"] = usuario["email"]
        return _json_sucesso("Login realizado!", nome=usuario["nome"])

    return _json_erro("Email ou senha incorretos!", 401)


@app.route("/api/logout", methods=["GET", "POST"])
def api_logout():
    session.clear()
    return redirect("/")


# ============================================================
# API — DISCIPLINAS
# ============================================================
@app.route("/api/disciplinas", methods=["GET"])
def api_listar_disciplinas():
    return jsonify(sistema.listar_disciplinas())

@app.route("/api/disciplinas", methods=["POST"])
def api_cadastrar_disciplina():
    dados = _validar_json()
    if not isinstance(dados, dict):
        return dados

    nome = (dados.get("nome") or "").strip()
    cor = (dados.get("cor") or "#093952").strip() or "#093952"

    if not nome:
        return _json_erro("Nome da disciplina é obrigatório.")

    resultado = sistema.cadastrar_disciplina(nome, cor)
    return jsonify(resultado)


@app.route("/api/disciplinas", methods=["PUT"])
def api_editar_disciplina():
    dados = _validar_json()
    if not isinstance(dados, dict):
        return dados

    nome_atual = (dados.get("nome_atual") or "").strip()
    novo_nome = (dados.get("novo_nome") or "").strip()
    nova_cor = (dados.get("nova_cor") or "").strip()

    if not nome_atual or not novo_nome or not nova_cor:
        return _json_erro("Nome atual, novo nome e nova cor são obrigatórios.")

    resultado = sistema.editar_disciplina(nome_atual, novo_nome, nova_cor)
    return jsonify(resultado)

@app.route("/api/disciplinas/<nome>", methods=["DELETE"])
def api_remover_disciplina(nome):
    resultado = sistema.remover_disciplina(nome)
    return jsonify(resultado)


# ============================================================
# API — TAREFAS
# ============================================================
@app.route("/api/tarefas", methods=["GET"])
def api_listar_tarefas():
    return jsonify(sistema.listar_tarefas())

@app.route("/api/tarefas", methods=["POST"])
def api_adicionar_tarefa():
    dados = _validar_json()
    if not isinstance(dados, dict):
        return dados

    nome = (dados.get("nome") or "").strip()
    if not nome:
        return _json_erro("Nome da tarefa é obrigatório.")

    resultado = sistema.adicionar_tarefa(nome)
    return jsonify(resultado)


@app.route("/api/tarefas/<int:index>/concluir", methods=["PUT"])
def api_concluir_tarefa(index):
    resultado = sistema.concluir_tarefa(index)
    return jsonify(resultado)

@app.route("/api/tarefas/<int:index>", methods=["DELETE"])
def api_remover_tarefa(index):
    resultado = sistema.remover_tarefa(index)
    return jsonify(resultado)


# ============================================================
# API — SESSÕES
# ============================================================
@app.route("/api/sessoes", methods=["GET"])
def api_listar_sessoes():
    return jsonify(sistema.listar_sessoes())

@app.route("/api/sessoes", methods=["POST"])
def api_registrar_sessao():
    dados = _validar_json()
    if not isinstance(dados, dict):
        return dados

    disciplina = (dados.get("disciplina") or "").strip()
    if not disciplina:
        return _json_erro("Disciplina é obrigatória para registrar uma sessão.")

    resultado = sistema.registrar_sessao(
        disciplina,
        dados.get("horas", 0),
        dados.get("minutos", 0),
        dados.get("data"),
        dados.get("foco", False)
    )
    return jsonify(resultado)

@app.route("/api/sessoes/<int:index>", methods=["DELETE"])
def api_remover_sessao(index):
    resultado = sistema.remover_sessao(index)
    return jsonify(resultado)


# ============================================================
# API — EVENTOS
# ============================================================
@app.route("/api/eventos", methods=["GET"])
def api_listar_eventos():
    return jsonify(sistema.listar_eventos())

@app.route("/api/eventos", methods=["POST"])
def api_adicionar_evento():
    dados = _validar_json()
    if not isinstance(dados, dict):
        return dados

    data = (dados.get("data") or "").strip()
    texto = (dados.get("texto") or "").strip()
    if not data or not texto:
        return _json_erro("Data e texto do evento são obrigatórios.")

    resultado = sistema.adicionar_evento(
        data,
        texto,
        dados.get("disciplina", "")
    )
    return jsonify(resultado)

@app.route("/api/eventos/<data>/<int:index>", methods=["DELETE"])
def api_remover_evento(data, index):
    resultado = sistema.remover_evento(data, index)
    return jsonify(resultado)


# ============================================================
# API — RELATÓRIO
# ============================================================
@app.route("/api/relatorio", methods=["GET"])
def api_relatorio():
    periodo = request.args.get("periodo", "semana")
    disciplina = request.args.get("disciplina")
    resultado = sistema.gerar_relatorio(periodo, disciplina)
    return jsonify(resultado)


# ============================================================
# API — BACKUP
# ============================================================
@app.route("/api/backup", methods=["GET"])
def api_exportar_backup():
    return jsonify(sistema.exportar_backup())

@app.route("/api/backup", methods=["POST"])
def api_importar_backup():
    dados = _validar_json()
    if not isinstance(dados, dict):
        return dados

    resultado = sistema.importar_backup(dados)
    return jsonify(resultado)

#============================================
#REDEFINIÇAO DE SENHA
#============================================

@app.route("/api/esqueci-senha", methods=["POST"])
def api_esqueci_senha():
    dados = _validar_json()
    if not isinstance(dados, dict):
        return dados

    email = (dados.get("email") or "").strip().lower()
    if not email:
        return _json_erro("Email é obrigatório para recuperar a senha.")

    usuario = next((u for u in sistema.dados["usuarios"] if u["email"].lower() == email), None)
    if not usuario:
        return _json_sucesso("Se o email estiver cadastrado, você receberá as instruções.")

    token = serializer.dumps(email, salt="recuperar-senha")
    link = url_for("redefinir_senha", token=token, _external=True)

    msg = Message(
        subject="Evolua — Redefinição de senha",
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[email],
        html=f"""
        <div style="font-family: 'League Spartan', sans-serif; max-width: 480px; margin: auto; padding: 32px; background: #f7f9fb; border-radius: 12px;">
            <h2 style="color: #093952;">Redefinir sua senha</h2>
            <p style="color: #555;">Recebemos uma solicitação para redefinir a senha da sua conta no <strong>Evolua</strong>.</p>
            <p style="color: #555;">Clique no botão abaixo para criar uma nova senha. O link expira em <strong>1 hora</strong>.</p>
            <a href="{link}" style="display:inline-block; margin: 20px 0; padding: 12px 24px; background: #093952; color: white; border-radius: 8px; text-decoration: none; font-weight: 700;">
                Redefinir senha
            </a>
            <p style="color: #aaa; font-size: 12px;">Se você não solicitou a redefinição, ignore este email.</p>
        </div>
        """
    )

    try:
        mail.send(msg)
    except Exception as exc:
        return _json_erro(f"Falha ao enviar email: {exc}", 500)

    return _json_sucesso("Email enviado com sucesso!")


@app.route("/redefinir-senha/<token>")
def redefinir_senha(token):
    try:
        email = serializer.loads(token, salt="recuperar-senha", max_age=3600)
    except:
        return render_template("login.html", erro="Link inválido ou expirado!")
    return render_template("redefinir-senha.html", token=token)


@app.route("/api/redefinir-senha", methods=["POST"])
def api_redefinir_senha():
    dados = _validar_json()
    if not isinstance(dados, dict):
        return dados

    token = dados.get("token")
    nova_senha = dados.get("senha")
    if not token or not nova_senha:
        return _json_erro("Token e nova senha são obrigatórios.")

    try:
        email = serializer.loads(token, salt="recuperar-senha", max_age=3600)
    except Exception:
        return _json_erro("Link inválido ou expirado!", 400)

    for u in sistema.dados["usuarios"]:
        if u["email"].lower() == email.lower():
            u["senha"] = generate_password_hash(nova_senha)
            sistema._salvar()
            return _json_sucesso("Senha redefinida com sucesso!")

    return _json_erro("Usuário não encontrado!", 404)


if __name__ == "__main__":
    app.run(debug=True)