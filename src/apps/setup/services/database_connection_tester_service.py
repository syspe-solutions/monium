import sqlite3
from pathlib import Path

from apps.setup.dtos.database_configuration_dto import DatabaseConfigurationDTO

_ROUNDTRIP_TABLE = "_monium_setup_connection_check"


class DatabaseConnectionTestError(Exception):
    """Levantada quando o instalador não consegue confirmar leitura/escrita na
    configuração de banco informada — mensagem já pronta pra exibir ao operador."""


class DatabaseConnectionTesterService:
    """Confirma que a configuração escolhida no instalador realmente funciona,
    fazendo um roundtrip de escrita/leitura (não só abrir a conexão) — credenciais
    corretas mas sem permissão de CREATE TABLE, por exemplo, falham aqui em vez de
    só durante o `migrate` depois do restart."""

    def test(self, configuration: DatabaseConfigurationDTO) -> None:
        if configuration.engine == "sqlite3":
            self._test_sqlite(configuration)
            return
        self._test_postgresql(configuration)

    def _test_sqlite(self, configuration: DatabaseConfigurationDTO) -> None:
        path = Path(configuration.name)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            connection = sqlite3.connect(configuration.name)
            self._roundtrip(connection, connection.cursor())
            connection.close()
        except (OSError, sqlite3.Error) as error:
            raise DatabaseConnectionTestError(
                f"Não foi possível escrever em '{configuration.name}': {error}"
            )

    def _test_postgresql(self, configuration: DatabaseConfigurationDTO) -> None:
        try:
            import psycopg2
        except ImportError:
            raise DatabaseConnectionTestError(
                "Driver do PostgreSQL (psycopg2) não está instalado nesta imagem."
            )

        try:
            connection = psycopg2.connect(
                host=configuration.host,
                port=configuration.port or 5432,
                dbname=configuration.name,
                user=configuration.user,
                password=configuration.password,
                connect_timeout=5,
            )
            connection.autocommit = True
            self._roundtrip(connection, connection.cursor())
            connection.close()
        except psycopg2.OperationalError as error:
            raise DatabaseConnectionTestError(
                f"Não foi possível conectar ao PostgreSQL: {error}"
            )
        except psycopg2.Error as error:
            raise DatabaseConnectionTestError(
                f"Conectou, mas a operação de teste falhou (permissões?): {error}"
            )

    def _roundtrip(self, connection, cursor) -> None:
        cursor.execute(f"CREATE TABLE {_ROUNDTRIP_TABLE} (id INTEGER)")
        cursor.execute(f"DROP TABLE {_ROUNDTRIP_TABLE}")
        connection.commit()
