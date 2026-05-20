import json
from models.models import Disciplina, Tarefa, Sessao, SessaoFoco, Evento, Relatorio


class SistemaEstudos:
    """Gerencia todas as operações do sistema Evolua (Implementa o padrão Singleton)."""

    # atributo privado de classe que armazena a única instancia ativa
    _instancia = None

    # o método __new__ intercepta a criação do objeto antes do __init__
    def __new__(cls, *args, **kwargs): 
        if cls._instancia is None: 
            # Se não houver instância criada, cria uma e guarda na variável de classe
            cls._instancia = super().__new__(cls)
        # retorna sempre a mesma instância guardada
        return cls._instancia 

    def __init__(self):
        # garante que o processo de inicialização e leitura do JSON ocorra apenas uma vez
        if not hasattr(self, '_inicializado'):
            self.arquivo = "data/dados.json"
            self.dados = self._carregar()
            self._inicializado = True

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

    def _salvar(self):
        with open(self.arquivo, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, indent=4, ensure_ascii=False)

    # -------------------- DISCIPLINAS --------------------
    def cadastrar_disciplina(self, nome: str, cor: str = "#093952") -> dict:
        for d in self.dados["disciplinas"]:
            if d["nome"] == nome:
                return {"erro": "Disciplina já existe!"}
        disciplina = Disciplina(nome, cor)
        self.dados["disciplinas"].append(disciplina.to_dict())
        self._salvar()
        return {"sucesso": "Disciplina cadastrada!", "disciplina": disciplina.to_dict()}

    def listar_disciplinas(self) -> list:
        return self.dados["disciplinas"]

    def editar_disciplina(self, nome_atual: str, novo_nome: str, nova_cor: str) -> dict:
        for d in self.dados["disciplinas"]:
            if d["nome"] == nome_atual:
                d["nome"] = novo_nome
                d["cor"] = nova_cor
                self._salvar()
                return {"sucesso": "Disciplina atualizada!"}
        return {"erro": "Disciplina não encontrada!"}

    def remover_disciplina(self, nome: str) -> dict:
        self.dados["disciplinas"] = [d for d in self.dados["disciplinas"] if d["nome"] != nome]
        self._salvar()
        return {"sucesso": "Disciplina removida!"}

    # -------------------- TAREFAS --------------------
    def adicionar_tarefa(self, nome: str) -> dict:
        tarefa = Tarefa(nome)
        self.dados["tarefas"].append(tarefa.to_dict())
        self._salvar()
        return {"sucesso": "Tarefa adicionada!", "tarefa": tarefa.to_dict()}

    def listar_tarefas(self) -> list:
        return self.dados["tarefas"]

    def concluir_tarefa(self, index: int) -> dict:
        try:
            self.dados["tarefas"][index]["concluida"] = True
            self._salvar()
            return {"sucesso": "Tarefa concluída!"}
        except IndexError:
            return {"erro": "Tarefa não encontrada!"}

    def remover_tarefa(self, index: int) -> dict:
        try:
            self.dados["tarefas"].pop(index)
            self._salvar()
            return {"sucesso": "Tarefa removida!"}
        except IndexError:
            return {"erro": "Tarefa não encontrada!"}

    # -------------------- SESSÕES --------------------
    def registrar_sessao(self, disciplina: str, horas: int, minutos: int, data: str = None, foco: bool = False) -> dict:
        if foco:
            sessao = SessaoFoco("Sessão Foco", disciplina, horas, minutos, data)
        else:
            sessao = Sessao("Sessão", disciplina, horas, minutos, data)

        # POLIMORFISMO — resumo() se adapta dinamicamente ao tipo de objeto instanciado
        print(f"[POLIMORFISMO] {sessao.resumo()}")

        self.dados["sessoes"].append(sessao.to_dict())
        self._salvar()
        return {"sucesso": "Sessão registrada!", "sessao": sessao.to_dict()}

    def listar_sessoes(self) -> list:
        return self.dados["sessoes"]

    def remover_sessao(self, index: int) -> dict:
        try:
            self.dados["sessoes"].pop(index)
            self._salvar()
            return {"sucesso": "Sessão removida!"}
        except IndexError:
            return {"erro": "Sessão não encontrada!"}

    # -------------------- EVENTOS --------------------
    def adicionar_evento(self, data: str, texto: str, disciplina: str = "") -> dict:
        evento = Evento(texto, data, disciplina)
        if data not in self.dados["eventos"]:
            self.dados["eventos"][data] = []
        self.dados["eventos"][data].append(evento.to_dict())
        self._salvar()
        return {"sucesso": "Evento adicionado!", "evento": evento.to_dict()}

    def listar_eventos(self) -> dict:
        return self.dados["eventos"]

    def remover_evento(self, data: str, index: int) -> dict:
        try:
            self.dados["eventos"][data].pop(index)
            if not self.dados["eventos"][data]:
                del self.dados["eventos"][data]
            self._salvar()
            return {"sucesso": "Evento removido!"}
        except:
            return {"erro": "Evento não encontrado!"}

    # -------------------- RELATÓRIO --------------------
    def gerar_relatorio(self, periodo: str = "semana", disciplina: str = None) -> dict:
        relatorio = Relatorio(self.dados["sessoes"])
        return relatorio.gerar(periodo, disciplina)

    # -------------------- BACKUP --------------------
    def exportar_backup(self) -> dict:
        return self.dados

    def importar_backup(self, dados: dict) -> dict:
        self.dados = dados
        self._salvar()
        return {"sucesso": "Backup importado!"}