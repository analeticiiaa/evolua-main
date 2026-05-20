from abc import ABC, abstractmethod
from datetime import datetime, timedelta

# ============================================================
# CLASSE ABSTRATA BASE — todos os itens herdam dela
# ============================================================
class ItemEstudo(ABC):
    """Classe abstrata que representa qualquer item do sistema."""

    def __init__(self, nome: str):
        self.nome = nome
        self.criado_em = datetime.now().strftime("%Y-%m-%d")

    @abstractmethod
    def to_dict(self) -> dict:
        """Método abstrato — toda subclasse DEVE implementar."""
        pass

    @abstractmethod
    def resumo(self) -> str:
        """Método abstrato — retorna um resumo do item."""
        pass

    def __str__(self):
        return f"{self.__class__.__name__}: {self.nome}"


# ============================================================
# HERANÇA — Classes filhas de ItemEstudo
# ============================================================

class Disciplina(ItemEstudo):
    """Representa uma disciplina de estudo."""

    def __init__(self, nome: str, cor: str = "#093952"):
        super().__init__(nome)
        self.cor = cor

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "cor": self.cor,
            "criado_em": self.criado_em
        }

    def resumo(self) -> str:
        return f"Disciplina: {self.nome} (cor: {self.cor})"


class Tarefa(ItemEstudo):
    """Representa uma tarefa a ser realizada."""

    def __init__(self, nome: str, concluida: bool = False):
        super().__init__(nome)
        self.concluida = concluida

    def concluir(self):
        self.concluida = True

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "concluida": self.concluida,
            "criado_em": self.criado_em
        }

    def resumo(self) -> str:
        status = "✔ Concluída" if self.concluida else "❌ Pendente"
        return f"Tarefa: {self.nome} [{status}]"


class Sessao(ItemEstudo):
    """Representa uma sessão de estudo registrada manualmente."""

    def __init__(self, nome: str, disciplina: str, horas: int = 0, minutos: int = 0, data: str = None):
        super().__init__(nome)
        self.disciplina = disciplina
        self.horas = horas
        self.minutos = minutos
        self.data = data or datetime.now().strftime("%Y-%m-%d")

    def duracao_total_minutos(self) -> int:
        return self.horas * 60 + self.minutos

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "disciplina": self.disciplina,
            "horas": self.horas,
            "minutos": self.minutos,
            "data": self.data
        }

    def resumo(self) -> str:
        return f"Sessão: {self.disciplina} | {self.horas}h {self.minutos}min | {self.data}"


class SessaoFoco(Sessao):
    """Representa uma sessão de foco (Pomodoro). Herda de Sessao."""

    def __init__(self, nome: str, disciplina: str, horas: int = 0, minutos: int = 25, data: str = None):
        super().__init__(nome, disciplina, horas, minutos, data)
        self.tipo = "foco"

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["tipo"] = self.tipo
        return base

    def resumo(self) -> str:
        return f"Sessão Foco: {self.disciplina} | {self.horas}h {self.minutos}min | {self.data} 🎯"


class Evento(ItemEstudo):
    """Representa um compromisso no calendário."""

    def __init__(self, nome: str, data: str, disciplina: str = ""):
        super().__init__(nome)
        self.data = data
        self.disciplina = disciplina

    def to_dict(self) -> dict:
        return {
            "texto": self.nome,
            "data": self.data,
            "disciplina": self.disciplina
        }

    def resumo(self) -> str:
        disc = f" ({self.disciplina})" if self.disciplina else ""
        return f"Compromisso: {self.nome}{disc} | {self.data}"


# ============================================================
# USUÁRIO
# ============================================================
class Usuario:
    """Representa um usuário do sistema."""

    def __init__(self, nome: str, email: str, senha: str):
        self.nome = nome
        self.email = email
        self.senha = senha

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "email": self.email,
            "senha": self.senha
        }

    def __str__(self):
        return f"Usuário: {self.nome} ({self.email})"


# ============================================================
# STRATEGY PATTERN — Algoritmos de Filtragem de Relatório
# ============================================================
#o padrão que elimina os ifs do seu código separando "o que o sistema faz" de "como ele faz".
class EstrategiaFiltroRelatorio(ABC): #obriga as demais classes a implemntarem o metodo filtrar
    """Interface comum para todas as estratégias de filtragem."""
    @abstractmethod
    def filtrar(self, sessoes: list) -> list:
        pass

#Cada uma implementa o seu próprio método filtrar com a sua lógica matemática específica de data
class FiltroDia(EstrategiaFiltroRelatorio):
    def filtrar(self, sessoes: list) -> list:
        limite = datetime.now().strftime("%Y-%m-%d")
        return [s for s in sessoes if s["data"] == limite]


class FiltroSemana(EstrategiaFiltroRelatorio):
    def filtrar(self, sessoes: list) -> list:
        limite = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        return [s for s in sessoes if s["data"] >= limite]


class FiltroMes(EstrategiaFiltroRelatorio):
    def filtrar(self, sessoes: list) -> list:
        limite = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        return [s for s in sessoes if s["data"] >= limite]


class FiltroTodos(EstrategiaFiltroRelatorio):
    def filtrar(self, sessoes: list) -> list:
        return sessoes


# CONTEXTO
class Relatorio:
    """Gera relatórios delegando a filtragem temporal para uma Strategy."""

    def __init__(self, sessoes: list):
        self.sessoes = sessoes
        # Mapeia os parâmetros recebidos em strings para os objetos Strategy
        self._estrategias = {
            "dia": FiltroDia(),
            "semana": FiltroSemana(),
            "mes": FiltroMes()
        }

    def gerar(self, periodo: str = "semana", disciplina: str = None) -> dict:
        #"Aqui esta o coração do padrao Strategy. Em vez de fazer um monte de if periodo == 'dia', eu busco a estratégia direto no dicionario e executo o filtro de forma polimórfica
        #O dicionário busca a classe correta dinamicamente
        estrategia = self._estrategias.get(periodo, FiltroTodos())
        #O polimorfismo acontece aqui: nao importa qual classe veio,
    # nos apenas chamamos o mtodo .filtrar() dela!
        filtradas = estrategia.filtrar(self.sessoes)

        if disciplina:
            filtradas = [s for s in filtradas if s["disciplina"] == disciplina]

        total_minutos = sum(s["horas"] * 60 + s["minutos"] for s in filtradas)

        return {
            "periodo": periodo,
            "disciplina": disciplina or "todas",
            "total_sessoes": len(filtradas),
            "total_minutos": total_minutos,
            "total_horas": round(total_minutos / 60, 2)
        }