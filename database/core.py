import collections
import asyncio
import abc
from typing import overload, Type

from .cache import Cache
from .models import DatabaseModel, _SampleModel


class Database(abc.ABC):
    """
    Classe abstrata para se comunicar com o banco de dados.

    Notas
    -----
    É necessário implementar os métodos:
    ```
    def _get_raw_data(...) -> dict: ...
        '''Retorna um dado do banco de dados.'''
    def _insert_raw_data(...) -> None: ...
        '''Inseri um dado no banco de dados.'''
    def _update_raw_data(...) -> None: ...
        '''Atualiza um dado no banco de dados.'''
    ```

    Utilize o parâmetro `models` para definir modelos para coleções
    diferentes, por exemplo:
    ```
    >>> models = {"players": models.Player,
    ...           "servers": models.Server}
    >>> db = Database(models)
    >>> player = await db.get_data("players", "Ashley")
    >>> print(player.name, player.level)
    Ashley 51
    ```
    Dessa forma você pode criar um modelo para cada coleção. Lembrando
    que no modelo acima, os modelos `Player` e `Server` são
    demonstrativos e precisam ser criados, veja `database.models` para
    criar um modelo.

    Parâmetros
    ----------
    models : dict

    Atributos
    ---------
    models : dict
    """
    def __init__(self, models: dict):
        self.models = models
        self.__cache = collections.defaultdict(Cache)
        self.cache = self.__cache

    def _format_filter(self, f) -> dict:
        if type(f) is not dict:
            raise TypeError("invalid filter, filter need to be a dict")
        return f

    def _transform_raw_data(self, data, from_):
        """
        Transforma um dado bruto em um modelo.

        Parâmetros
        ----------
        data : dict
        from_ : str
            Coleção da onde o dado veio.

        Retornos
        --------
        typing.Type[DatabaseModel]
        """
        model = self.models.get(from_, _SampleModel)
        return model.from_dict(self, data)

    async def get_data(self, c, filter):
        """
        Retorna um dado de id `data_id` na coleção `c`.

        Parâmetros
        ----------
        c : str
            Coleção onde o dado será procurado.
        filter : typing.Any
            Filtro do dado que será buscado.

        Retornos
        --------
        typing.Union[Type[DatabaseModel], None]
            Retorna Type[DatabaseModel] se encontrar, caso contrário
            retorna `None`.
        """
        filter = self._format_filter(filter)

        data = await self._get_cache_data(c, filter)

        if not data:
            data = await self._get_raw_data(c, filter)

            if data:
                data = self._transform_raw_data(data, c)

            await self._insert_into_cache(c, data)

        return data

    async def _get_cache_data(self, c, filter):
        """
        Retorna um dado de id `data_id` na coleção `c` em cache.

        Parâmetros
        ----------
        c : str
            Coleção onde o dado será procurado.
        filter : typing.Any
            Filtro do dado que será buscado.

        Retornos
        --------
        typing.Union[Type[DatabaseModel], None]
            Retorna Type[DatabaseModel] se encontrar, caso contrário
            retorna `None`.
        """
        c = self.__cache[c]
        for data in c:
            if data._validates(filter):
                break
        else:
            data = None
        return await asyncio.sleep(0, result=data)

    @abc.abstractmethod
    async def _get_raw_data(self, c, filter) -> dict:
        """
        Retorna um dado direto do banco de dados. Retorna `None` se nada
        econtrado.

        Parâmetros
        ----------
        c : str
            Coleção da onde o dado será pego.
        filter : typing.Any
            Filtro do dado que será pego.

        Retornos
        --------
        typing.Union[dict, None]
            Os dados pegos.
        """
        ...

    @overload
    async def _insert_into_cache(self, c, data: dict) -> Type[DatabaseModel]:
        ...

    @overload
    async def _insert_into_cache(self, c, data: Type[DatabaseModel]) -> None:
        ...

    async def _insert_into_cache(self, c, data):
        """
        Insere um dado no cache.

        Parâmetros
        ----------
        c : str
            Coleção onde o dado será colocado.
        data : typing.Union[typing.Type[DatabaseModel], dict]
            Dado que será inserido.

        Retornos
        --------
        typing.Union[Type[DatabaseModel], None]
            Retorna um Type[DatabaseModel] se `data` for um `dict`, caso
            contrário retorna `None`.
        """
        return_data = data
        if type(data) is dict:
            data = self._transform_raw_data(data, c)
            return_data = None

        self.__cache[c].push(data)

        return await asyncio.sleep(0, result=return_data)

    @abc.abstractmethod
    async def _insert_raw_data(self, c, data: dict):
        """
        Insere um dado bruto direto no banco de dados.

        Parâmetros
        ----------
        c : str
            Coleção da onde o dado será inserido.
        data : dict
            Dado que será inserido.
        """
        ...

    @overload
    async def insert_data(self, c, data: dict) -> Type[DatabaseModel]: ...
    @overload
    async def insert_data(self, c, data: Type[DatabaseModel]) -> None: ...

    async def insert_data(self, c, data):
        """
        Insere um dado.

        Parâmetros
        ----------
        c : str
            Coleção onde o dado será colocado.
        data : typing.Union[typing.Type[DatabaseModel], dict]
            Dado que será inserido.

        Retornos
        --------
        typing.Union[Type[DatabaseModel], None]
            Retorna um Type[DatabaseModel] se `data` for um `dict`, caso
            contrário retorna `None`.
        """
        result = await self._insert_into_cache(c, data)
        data = data.to_dict() if result is not None else data
        await self._insert_raw_data(c, data)
        return await asyncio.sleep(0, result=result)

    @overload
    async def _update_cache_data(self, c, filter,
                                 new_data: dict) -> Type[DatabaseModel]: ...

    @overload
    async def _update_cache_data(self, c, filter,
                                 new_data: Type[DatabaseModel]) -> None: ...

    async def _update_cache_data(self, c, filter, new_data):
        """
        Atualiza um dado que está no cache.

        Parâmetros
        ----------
        c : str
            Coleção onde o dado está.
        filter : typing.Any
            Filtro do dado que será atualizado.
        new_data : typing.Union[typing.Type[DatabaseModel], dict]
            Novos dados.

        Retornos
        --------
        typing.Union[Type[DatabaseModel], None]
            Retorna um Type[DatabaseModel] se `new_data` for um `dict`,
            caso contrário retorna `None`.
        """
        return_data = None
        if type(new_data) is dict:
            new_data = self._transform_raw_data(new_data, c)
            return_data = new_data

        c = self.__cache[c]
        for index, data in enumerate(c):
            if data._validates(filter):
                c.replace(index, to=new_data)

        return await asyncio.sleep(0, result=return_data)

    @abc.abstractmethod
    async def _update_raw_data(self, c, filter, new_data: dict):
        """
        Atualiza um dado direto no banco de dados.

        Parâmetros
        ----------
        c : str
            Coleção aonde o dado será atualizado.
        filter : typing.Any
            Filtro do dado que será atualizado.
        new_data : dict
            Novos dados.
        """
        ...

    @overload
    async def update_data(self, c, filter,
                          new_data: dict) -> Type[DatabaseModel]: ...

    @overload
    async def update_data(self, c, filter,
                          new_data: Type[DatabaseModel]) -> None: ...

    async def update_data(self, c, filter, new_data):
        """
        Atualiza um dado.

        Parâmetros
        ----------
        c : str
            Coleção onde o dado está.
        filter : typing.Any
            Filtro do dado que será atualizado.
        new_data : typing.Union[typing.Type[DatabaseModel], dict]
            Novos dados.

        Retornos
        --------
        typing.Union[Type[DatabaseModel], None]
            Retorna um Type[DatabaseModel] se `new_data` for um `dict`,
            caso contrário retorna `None`.
        """
        result = await self._update_cache_data(c, filter, new_data)
        new_data = new_data.to_dict() if result is None else new_data
        await self._update_raw_data(c, filter, new_data)
        return await asyncio.sleep(0, result=result)
=======
import collections
import asyncio
import abc
from typing import overload, Type

from .cache import Cache
from .models import DatabaseModel, _SampleModel


class Database(abc.ABC):
    """
    Classe abstrata para se comunicar com o banco de dados.

    Notas
    -----
    É necessário implementar os métodos:
    ```
    def _get_raw_data(...) -> dict: ...
        '''Retorna um dado do banco de dados.'''
    def _insert_raw_data(...) -> None: ...
        '''Inseri um dado no banco de dados.'''
    def _update_raw_data(...) -> None: ...
        '''Atualiza um dado no banco de dados.'''
    ```

    Utilize o parâmetro `models` para definir modelos para coleções
    diferentes, por exemplo:
    ```
    >>> models = {"players": models.Player,
    ...           "servers": models.Server}
    >>> db = Database(models)
    >>> player = await db.get_data("players", "Ashley")
    >>> print(player.name, player.level)
    Ashley 51
    ```
    Dessa forma você pode criar um modelo para cada coleção. Lembrando
    que no modelo acima, os modelos `Player` e `Server` são
    demonstrativos e precisam ser criados, veja `database.models` para
    criar um modelo.

    Parâmetros
    ----------
    models : dict

    Atributos
    ---------
    models : dict
    """
    def __init__(self, models: dict):
        self.models = models
        self.__cache = collections.defaultdict(Cache)

    def _format_filter(self, f) -> dict:
        if type(f) is not dict:
            raise TypeError("invalid filter, filter need to be a dict")
        return f

    def _transform_raw_data(self, data, from_):
        """
        Transforma um dado bruto em um modelo.

        Parâmetros
        ----------
        data : dict
        from_ : str
            Coleção da onde o dado veio.

        Retornos
        --------
        typing.Type[DatabaseModel]
        """
        model = self.models.get(from_, _SampleModel)
        return model.from_dict(self, data)

    async def get_data(self, c, filter):
        """
        Retorna um dado de id `data_id` na coleção `c`.

        Parâmetros
        ----------
        c : str
            Coleção onde o dado será procurado.
        filter : typing.Any
            Filtro do dado que será buscado.

        Retornos
        --------
        typing.Union[Type[DatabaseModel], None]
            Retorna Type[DatabaseModel] se encontrar, caso contrário
            retorna `None`.
        """
        filter = self._format_filter(filter)

        data = await self._get_cache_data(c, filter)

        if not data:
            data = await self._get_raw_data(c, filter)

            if data:
                data = self._transform_raw_data(data, c)

        return data

    async def _get_cache_data(self, c, filter):
        """
        Retorna um dado de id `data_id` na coleção `c` em cache.

        Parâmetros
        ----------
        c : str
            Coleção onde o dado será procurado.
        filter : typing.Any
            Filtro do dado que será buscado.

        Retornos
        --------
        typing.Union[Type[DatabaseModel], None]
            Retorna Type[DatabaseModel] se encontrar, caso contrário
            retorna `None`.
        """
        c = self.__cache[c]
        for data in c:
            for key, value in filter.items():
                try:
                    if data[key] == value:
                        break
                except KeyError:
                    continue
        else:
            data = None

        return await asyncio.sleep(0, result=data)

    @abc.abstractmethod
    async def _get_raw_data(self, c, filter) -> dict:
        """
        Retorna um dado direto do banco de dados. Retorna `None` se nada
        econtrado.

        Parâmetros
        ----------
        c : str
            Coleção da onde o dado será pego.
        filter : typing.Any
            Filtro do dado que será pego.

        Retornos
        --------
        typing.Union[dict, None]
            Os dados pegos.
        """
        ...

    @overload
    async def _insert_into_cache(self, c, data: dict) -> Type[DatabaseModel]:
        ...

    @overload
    async def _insert_into_cache(self, c, data: Type[DatabaseModel]) -> None:
        ...

    async def _insert_into_cache(self, c, data):
        """
        Insere um dado no cache.

        Parâmetros
        ----------
        c : str
            Coleção onde o dado será colocado.
        data : typing.Union[typing.Type[DatabaseModel], dict]
            Dado que será inserido.

        Retornos
        --------
        typing.Union[Type[DatabaseModel], None]
            Retorna um Type[DatabaseModel] se `data` for um `dict`, caso
            contrário retorna `None`.
        """
        return_data = data
        if type(data) is dict:
            data = self._transform_raw_data(data, c)
            return_data = None

        c = self.__cache[c]
        c.add(data.id, data)

        return return_data

    @abc.abstractmethod
    async def _insert_raw_data(self, c, data: dict):
        """
        Insere um dado bruto direto no banco de dados.

        Parâmetros
        ----------
        c : str
            Coleção da onde o dado será inserido.
        data : dict
            Dado que será inserido.
        """
        ...

    @overload
    async def insert_data(self, c, data: dict) -> Type[DatabaseModel]: ...
    @overload
    async def insert_data(self, c, data: Type[DatabaseModel]) -> None: ...

    async def insert_data(self, c, data):
        """
        Insere um dado.

        Parâmetros
        ----------
        c : str
            Coleção onde o dado será colocado.
        data : typing.Union[typing.Type[DatabaseModel], dict]
            Dado que será inserido.

        Retornos
        --------
        typing.Union[Type[DatabaseModel], None]
            Retorna um Type[DatabaseModel] se `data` for um `dict`, caso
            contrário retorna `None`.
        """
        result = await self._insert_into_cache(c, data)
        data = data.to_dict() if result is not None else data
        await self._insert_raw_data(c, data)
        return await asyncio.sleep(0, result=result)

    @overload
    async def _update_cache_data(self, c, filter,
                                 new_data: dict) -> Type[DatabaseModel]: ...

    @overload
    async def _update_cache_data(self, c, filter,
                                 new_data: Type[DatabaseModel]) -> None: ...

    async def _update_cache_data(self, c, filter, new_data):
        """
        Atualiza um dado que está no cache.

        Parâmetros
        ----------
        c : str
            Coleção onde o dado está.
        filter : typing.Any
            Filtro do dado que será atualizado.
        new_data : typing.Union[typing.Type[DatabaseModel], dict]
            Novos dados.

        Retornos
        --------
        typing.Union[Type[DatabaseModel], None]
            Retorna um Type[DatabaseModel] se `new_data` for um `dict`,
            caso contrário retorna `None`.
        """
        return

        c = self.__cache[c]
        try:
            del c[data_id]
        except KeyError:
            pass

        return_data = None
        if type(new_data) is dict:
            new_data = self._transform_raw_data(new_data, c)
            return_data = new_data

        c[data_id] = new_data

        return await asyncio.sleep(0, result=return_data)

    @abc.abstractmethod
    async def _update_raw_data(self, c, filter, new_data: dict):
        """
        Atualiza um dado direto no banco de dados.

        Parâmetros
        ----------
        c : str
            Coleção aonde o dado será atualizado.
        filter : typing.Any
            Filtro do dado que será atualizado.
        new_data : dict
            Novos dados.
        """
        ...

    @overload
    async def update_data(self, c, filter,
                          new_data: dict) -> Type[DatabaseModel]: ...

    @overload
    async def update_data(self, c, filter,
                          new_data: Type[DatabaseModel]) -> None: ...

    async def update_data(self, c, filter, new_data):
        """
        Atualiza um dado.

        Parâmetros
        ----------
        c : str
            Coleção onde o dado está.
        filter : typing.Any
            Filtro do dado que será atualizado.
        new_data : typing.Union[typing.Type[DatabaseModel], dict]
            Novos dados.

        Retornos
        --------
        typing.Union[Type[DatabaseModel], None]
            Retorna um Type[DatabaseModel] se `new_data` for um `dict`,
            caso contrário retorna `None`.
        """
        result = await self._update_cache_data(c, filter, new_data)
        new_data = new_data.to_dict() if result is None else new_data
        await self._update_raw_data(c, filter, new_data)
        return await asyncio.sleep(0, result=result)
