import json
from models.models import Disciplina, Tarefa, Sessao, SessaoFoco, Evento, Relatorio

# ============================================================
# SUBSISTEMAS — Classes focadas em responsabilidades únicas
# ============================================================

class GerenciadorDados:
    """Subsistema isolado responsável pelo armazenamento e leitura do JSON."""
    def __init__(self, arquivo="data/dados.json"):
        self.arquivo = arquivo
        self.dados = self._carregar()

    def _carregar(self) -> dict:
        try:
            with open(self.arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {
                "usuarios": [],
                "disciplinas": [],
                "sessoes": [],
                "tarefas": [],
                "eventos": {}
            }

    def salvar(self):
        with open(self.arquivo, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, indent=4, ensure_ascii=False)

# --- SUBSISTEMA OCULTO  ---
class SubsistemaDisciplinas:
    def __init__(self, db: GerenciadorDados):
        self.db = db
# Toda a lógica complexa de validação e salvamento fica aqui
    def cadastrar(self, nome: str, cor: str) -> dict:
        for d in self.db.dados["disciplinas"]:
            if d["nome"] == nome:
                return {"erro": "Disciplina já existe!"}
        disciplina = Disciplina(nome, cor)
        self.db.dados["disciplinas"].append(disciplina.to_dict())
        self.db.salvar()
        return {"sucesso": "Disciplina cadastrada!", "disciplina": disciplina.to_dict()}

    def listar(self) -> list:
        return self.db.dados["disciplinas"]

    def editar(self, nome_atual: str, novo_nome: str, nova_cor: str) -> dict:
        for d in self.db.dados["disciplinas"]:
            if d["nome"] == nome_atual:
                d["nome"] = novo_nome
                d["cor"] = nova_cor
                self.db.salvar()
                return {"sucesso": "Disciplina atualizada!"}
        return {"erro": "Disciplina não encontrada!"}

    def remover(self, nome: str) -> dict:
        self.db.dados["disciplinas"] = [d for d in self.db.dados["disciplinas"] if d["nome"] != nome]
        self.db.salvar()
        return {"sucesso": "Disciplina removida!"}


class SubsistemaTarefas:
    def __init__(self, db: GerenciadorDados):
        self.db = db

    def adicionar(self, nome: str) -> dict:
        tarefa = Tarefa(nome)
        self.db.dados["tarefas"].append(tarefa.to_dict())
        self.db.salvar()
        return {"sucesso": "Tarefa adicionada!", "tarefa": tarefa.to_dict()}

    def listar(self) -> list:
        return self.db.dados["tarefas"]

    def concluir(self, index: int) -> dict:
        try:
            self.db.dados["tarefas"][index]["concluida"] = True
            self.db.salvar()
            return {"sucesso": "Tarefa concluída!"}
        except IndexError:
            return {"erro": "Tarefa não encontrada!"}

    def remover(self, index: int) -> dict:
        try:
            self.db.dados["tarefas"].pop(index)
            self.db.salvar()
            return {"sucesso": "Tarefa removida!"}
        except IndexError:
            return {"erro": "Tarefa não encontrada!"}


class SubsistemaSessoes:
    def __init__(self, db: GerenciadorDados):
        self.db = db

    def registrar(self, disciplina: str, horas: int, minutes: int, data: str = None, foco: bool = False) -> dict:
        if foco:
            sessao = SessaoFoco("Sessão Foco", disciplina, horas, minutes, data)
        else:
            sessao = Sessao("Sessão", disciplina, horas, minutes, data)

        print(f"[POLIMORFISMO] {sessao.resumo()}")
        self.db.dados["sessoes"].append(sessao.to_dict())
        self.db.salvar()
        return {"sucesso": "Sessão registrada!", "sessao": sessao.to_dict()}

    def listar(self) -> list:
        return self.db.dados["sessoes"]

    def remover(self, index: int) -> dict:
        try:
            self.db.dados["sessoes"].pop(index)
            self.db.salvar()
            return {"sucesso": "Sessão removida!"}
        except IndexError:
            return {"erro": "Sessão não encontrada!"}


class SubsistemaEventos:
    def __init__(self, db: GerenciadorDados):
        self.db = db

    def adicionar(self, data: str, texto: str, disciplina: str = "") -> dict:
        evento = Evento(texto, data, disciplina)
        if data not in self.db.dados["eventos"]:
            self.db.dados["eventos"][data] = []
        self.db.dados["eventos"][data].append(evento.to_dict())
        self.db.salvar()
        return {"sucesso": "Evento adicionado!", "evento": evento.to_dict()}

    def listar(self) -> dict:
        return self.db.dados["eventos"]

    def remover(self, data: str, index: int) -> dict:
        try:
            self.db.dados["eventos"][data].pop(index)
            if not self.db.dados["eventos"][data]:
                del self.db.dados["eventos"][data]
            self.db.salvar()
            return {"sucesso": "Evento removido!"}
        except:
            return {"erro": "Evento não encontrado!"}


# ============================================================
# FACADE — Ponto de Entrada único unificado (Mantém o Singleton)
# ============================================================
class SistemaEstudos:
    """Age como uma Facade estrutural para simplificar as chamadas da API do Flask."""

    _instancia = None  #instancia comeca vazia, o que garante que a primeira chamada a SistemaEstudos() criara a instancia, e as seguintes retornarao a msm instancia

    def __new__(cls, *args, **kwargs): #O método __new__ controla a criação do objeto
        if cls._instancia is None: 
            #Se não existir, cria a primeira e única instância
            cls._instancia = super().__new__(cls)
            #Se já existir, devolve a mesma que já estava na memória
        return cls._instancia 

    def __init__(self):
        if not hasattr(self, '_inicializado'):
            # A Facade cria e gerencia o subsistema internamente
            self._db = GerenciadorDados()
            
            # Atalho público mantido ativo para garantir compatibilidade com as rotas de usuários do app.py
            self.dados = self._db.dados 

           
            self._subsistema_disciplinas = SubsistemaDisciplinas(self._db)
            self._subsistema_tarefas = SubsistemaTarefas(self._db)
            self._subsistema_sessoes = SubsistemaSessoes(self._db)
            self._subsistema_eventos = SubsistemaEventos(self._db)

            self._inicializado = True

    def _salvar(self):
        self._db.salvar()

    # -------------------- DISCIPLINAS --------------------
    def cadastrar_disciplina(self, nome: str, cor: str = "#093952") -> dict:
        # a Facade apenas DELEGA o trabalho para o subsistema responsável
        return self._subsistema_disciplinas.cadastrar(nome, cor)

    def listar_disciplinas(self) -> list:
        return self._subsistema_disciplinas.listar()

    def editar_disciplina(self, nome_atual: str, novo_nome: str, nova_cor: str) -> dict:
        return self._subsistema_disciplinas.editar(nome_atual, novo_nome, nova_cor)

    def remover_disciplina(self, nome: str) -> dict:
        return self._subsistema_disciplinas.remover(nome)

    # -------------------- TAREFAS --------------------
    def adicionar_tarefa(self, nome: str) -> dict:
        return self._subsistema_tarefas.adicionar(nome)

    def listar_tarefas(self) -> list:
        return self._subsistema_tarefas.listar()

    def concluir_tarefa(self, index: int) -> dict:
        return self._subsistema_tarefas.concluir(index)

    def remover_tarefa(self, index: int) -> dict:
        return self._subsistema_tarefas.remover(index)

    # -------------------- SESSÕES --------------------
    def registrar_sessao(self, disciplina: str, horas: int, minutos: int, data: str = None, foco: bool = False) -> dict:
        return self._subsistema_sessoes.registrar(disciplina, horas, minutos, data, foco)

    def listar_sessoes(self) -> list:
        return self._subsistema_sessoes.listar()

    def remover_sessao(self, index: int) -> dict:
        return self._subsistema_sessoes.remover(index)

    # -------------------- EVENTOS --------------------
    def adicionar_evento(self, data: str, texto: str, disciplina: str = "") -> dict:
        return self._subsistema_eventos.adicionar(data, texto, disciplina)

    def listar_eventos(self) -> dict:
        return self._subsistema_eventos.listar()

    def remover_evento(self, data: str, index: int) -> dict:
        return self._subsistema_eventos.remover(data, index)

    # -------------------- RELATÓRIO (Strategy) --------------------
    def gerar_relatorio(self, periodo: str = "semana", disciplina: str = None) -> dict:
        relatorio = Relatorio(self.dados["sessoes"])
        return relatorio.gerar(periodo, disciplina)

    # -------------------- BACKUP --------------------
    def exportar_backup(self) -> dict:
        return self.dados

    def importar_backup(self, dados: dict) -> dict:
        self._db.dados = dados
        self.dados = dados
        self._db.salvar()
        return {"sucesso": "Backup importado!"}