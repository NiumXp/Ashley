import inspect

_PREFIX = "_db"


class DatabaseModel:
    """
    Estrutura para criar um modelo para o banco de dados.

    Notas
    -----
    Você pode utilizar o atributo `state` para ter acesso a classe do
    banco de dados e implementar funções que atualize os dados
    diretamente para o banco de dados.

    Utilize o método `define` para definir uma atributo e `get` para
    pega-lo, é necessário fazer isso já que o método `to_dict` extrai
    todos os atributos definidos através do `define` e os retorna em um
    `dict`.

    Exemplos
    --------
    ```
    >>> class Player(DatabaseModel):
    ...     def __init__(self, state, data):
    ...         super().__init__(state, data)
    ...         self.define("name", data["name"])
    ...         self.define("level", data.get("level", 1))
    ...     @property
    ...     def name(self) -> str:
    ...         '''Retorna o nome do jogador.'''
    ...         return self.get("name")
    ...     @property
    ...     def level(self) -> int:
    ...         '''Retorna o level do jogador.'''
    ...         return self.get("level")
    ...     @level.setter
    ...     def level(self, new_value):
    ...         if self.get("level") < new_value:
    ...             self.edit("level", new_value)
    ```

    Parâmetros
    ----------
    state : typing.Type[Database]
        Estrutura do banco de dados.
    raw_data : dict
        Dados brutos do modelo.

    Atributos
    ---------
    state : typing.Type[Database]
        Estrutura do banco de dados.

    Raises
    ------
    KeyError
        `raw_data` não possui uma chave `_id`.
    """

    def __init__(self, state, raw_data: dict, ):
        self.state = state

        # Gera `KeyError` se `_id` não foi definido.
        self.define("_id", raw_data["_id"])

    def _validates(self, filter):
        """Diz se o objeto valida `filter`.
        Diz se o objeto corresponde com as informações de `filter`."""
        for k, v in filter.items():
            try:
                if self.get(k) == v:
                    continue
                return False
            except KeyError:
                return False
        # Se o `for` não rodar significa que `filter` == `{}`, logo,
        # esse objeto corresponde ao filtro.
        return True

    def define(self, name, value):
        """
        Define um atributo no modelo.

        Parâmetros
        ----------
        name : str
            Nome do atributo.
        value : typing.Any
            Valor do atributo.
        """
        name = _PREFIX + name
        self.__dict__[name] = value

    def edit(self, name, value):
        """Alias para `define`."""
        self.define(name, value)

    def get(self, name):
        """
        Retorna um atributo do modelo.

        Parâmetros
        ----------
        name : str
            Nome do atributo.

        Raises
        ------
        KeyError
            Nenhum atributo encontrado.

        Retorno
        -------
        typing.Any"""
        name = _PREFIX + name
        return self.__dict__[name]

    @property
    def id(self):
        """Id do modelo."""
        return self.get("_id")

    @classmethod
    def from_dict(cls, data: dict, state):
        """Retorna uma instância da classe baseada em `data`."""
        return cls(data, state)

    def to_dict(self) -> dict:
        """Retorna os dados brutos do modelo."""
        data = {}

        for name, member in inspect.getmembers(self):
            if name.startswith(_PREFIX):
                if member:  # Calls `__bool__` of the object.
                    name = name[len(_PREFIX):]
                    data[name] = member

        return data


class _SampleModel:
    _validates = DatabaseModel._validates

    def __init__(self, _, raw_data: dict):
        self.id = raw_data["_id"]

        cls = type(self)
        for k, v in raw_data.items():
            if type(v) is dict:
                raw_data[k] = cls(None, v)

        self.__dict__.update(raw_data)

    def __setattr__(self, name, value):
        if name not in self.__dict__:
            raise AttributeError("you can't define a new attribute")

        self.__dict__[name] = value

    @classmethod
    def from_dict(cls, _, data):
        return cls(_, data)

    def to_dict(self):
        return self.__dict__.copy()

    def __repr__(self) -> str:
        return f"<_SampleModel {self.__dict__!s}>"
=======
import inspect

_PREFIX = "_db"


class DatabaseModel:
    """
    Estrutura para criar um modelo para o banco de dados.

    Notas
    -----
    Você pode utilizar o atributo `state` para ter acesso a classe do
    banco de dados e implementar funções que atualize os dados
    diretamente para o banco de dados.

    Utilize o método `define` para definir uma atributo e `get` para
    pega-lo, é necessário fazer isso já que o método `to_dict` extrai
    todos os atributos definidos através do `define` e os retorna em um
    `dict`.

    Exemplos
    --------
    ```
    >>> class Player(DatabaseModel):
    ...     def __init__(self, state, data):
    ...         super().__init__(state, data)
    ...         self.define("name", data["name"])
    ...         self.define("level", data.get("level", 1))
    ...     @property
    ...     def name(self) -> str:
    ...         '''Retorna o nome do jogador.'''
    ...         return self.get("name")
    ...     @property
    ...     def level(self) -> int:
    ...         '''Retorna o level do jogador.'''
    ...         return self.get("level")
    ...     @level.setter
    ...     def level(self, new_value):
    ...         if self.get("level") < new_value:
    ...             self.edit("level", new_value)
    ```

    Parâmetros
    ----------
    state : typing.Type[Database]
        Estrutura do banco de dados.
    raw_data : dict
        Dados brutos do modelo.

    Atributos
    ---------
    state : typing.Type[Database]
        Estrutura do banco de dados.

    Raises
    ------
    KeyError
        `raw_data` não possui uma chave `_id`.
    """

    def __init__(self, state, raw_data: dict, ):
        self.state = state

        # Gera `KeyError` se `_id` não foi definido.
        self.define("_id", raw_data["_id"])

    def define(self, name, value):
        """
        Define um atributo no modelo.

        Parâmetros
        ----------
        name : str
            Nome do atributo.
        value : typing.Any
            Valor do atributo.
        """
        name = _PREFIX + name
        self.__dict__[name] = value

    def edit(self, name, value):
        """Alias para `define`."""
        self.define(name, value)

    def get(self, name):
        """
        Retorna um atributo do modelo.

        Parâmetros
        ----------
        name : str
            Nome do atributo.

        Retorno
        -------
        typing.Any"""
        name = _PREFIX + name
        return self.__dict__[name]

    @property
    def id(self):
        """Id do modelo."""
        return self.get("_id")

    @classmethod
    def from_dict(cls, data: dict, state):
        """Retorna uma instância da classe baseada em `data`."""
        return cls(data, state)

    def to_dict(self) -> dict:
        """Retorna os dados brutos do modelo."""
        data = {}

        for name, member in inspect.getmembers(self):
            if name.startswith(_PREFIX):
                if member:  # Calls `__bool__` of the object.
                    name = name[len(_PREFIX):]
                    data[name] = member

        return data


class _SampleModel:
    def __init__(self, _, raw_data: dict):
        self.id = raw_data["_id"]

        cls = type(self)
        for k, v in raw_data.items():
            if type(v) is dict:
                raw_data[k] = cls(None, v)

        self.__dict__.update(raw_data)

    def __setattr__(self, name, value):
        if name not in self.__dict__:
            raise AttributeError("you can't define a new attribute")

        self.__dict__[name] = value

    @classmethod
    def from_dict(cls, _, data):
        return cls(_, data)

    def to_dict(self):
        return self.__dict__.copy()

    def __repr__(self) -> str:
        return f"<_SampleModel {self.__dict__!s}>"
