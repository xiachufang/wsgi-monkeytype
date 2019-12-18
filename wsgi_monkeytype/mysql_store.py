import datetime
import logging

import MySQLdb

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from typing import Iterable, Optional, List, Union, Tuple
from DBUtils.PersistentDB import PersistentDB
from DBUtils.SteadyDB import SteadyDBConnection
from monkeytype import Config
from monkeytype.encoding import serialize_traces, CallTraceRow
from monkeytype.typing import DEFAULT_REWRITER, TypeRewriter
from monkeytype.db.base import CallTraceStore, CallTraceThunk
from monkeytype.tracing import CallTrace, CodeFilter
from monkeytype.config import default_code_filter

DEFAULT_TABLE = 'monkeytype_call_traces'
QueryValue = Union[str, int]
ParameterizedQuery = Tuple[str, List[QueryValue]]


logger = logging.getLogger("wsgi_monkeytype.mysql_store")


def create_call_trace_table(conn: SteadyDBConnection, table: str = DEFAULT_TABLE) -> None:
    query = """
CREATE TABLE IF NOT EXISTS {table} (
  id int(11) unsigned NOT NULL AUTO_INCREMENT,
  created_at  date,
  module      varchar(128),
  qualname    text,
  arg_types   mediumtext,
  return_type mediumtext,
  yield_type  mediumtext,
  PRIMARY KEY(id),
  KEY idx_module (module(12))
  );
""".format(table=table)
    with conn:
        cur = conn.cursor()
        cur.execute('SET sql_notes = 0;')
        cur.execute(query)
        cur.execute('SET sql_notes = 1;')


def parse_connection_string_to_dict(url):
    parsed = urlparse(url)
    path_parts = parsed.path[1:].split('?')
    connect_kwargs = {'database': path_parts[0]}
    if parsed.username:
        connect_kwargs['user'] = parsed.username
    if parsed.password:
        connect_kwargs['passwd'] = parsed.password
    if parsed.hostname:
        connect_kwargs['host'] = parsed.hostname
    if parsed.port:
        connect_kwargs['port'] = parsed.port
    return connect_kwargs


def make_query(table: str, module: str, qualname: Optional[str], limit: int) -> ParameterizedQuery:
    raw_query = """
    SELECT
        module, qualname, arg_types, return_type, yield_type
    FROM {table}
    WHERE
        module = %s
    """.format(table=table)
    values: List[QueryValue] = [module]
    if qualname is not None:
        raw_query += " AND qualname LIKE %s || '%'"
        values.append(qualname)
    raw_query += """
    GROUP BY
        module, qualname, arg_types, return_type, yield_type
    ORDER BY created_at DESC
    LIMIT %s
    """
    values.append(limit)
    return raw_query, values


class MySQLStore(CallTraceStore):

    def __init__(self, connection_string: str, table: str = DEFAULT_TABLE):
        self.table = table
        self._conn: Optional[SteadyDBConnection] = None
        self.connection_string = connection_string

    @property
    def conn(self):
        if self._conn is not None:
            return self._conn
        self._conn = PersistentDB(MySQLdb, **parse_connection_string_to_dict(self.connection_string)).connection()
        create_call_trace_table(self._conn, self.table)
        return self._conn

    @classmethod
    def make_store(cls, connection_string: str) -> CallTraceStore:
        return cls(connection_string)

    def list_modules(self) -> List[str]:
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("""SELECT distinct module FROM {table}""".format(table=self.table))
            return [row[0] for row in cur.fetchall() if row[0]]

    def filter(self, module: str, qualname_prefix: Optional[str] = None, limit: int = 2000) -> List[CallTraceThunk]:
        sql_query, values = make_query(self.table, module, qualname_prefix, limit)
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(sql_query, values)
            return [CallTraceRow(*row) for row in cur.fetchall()]

    def add(self, traces: Iterable[CallTrace]) -> None:
        values = []
        today = datetime.datetime.now().date()
        for row in serialize_traces(traces):
            values.append((today, row.module, row.qualname,
                           row.arg_types, row.return_type, row.yield_type))
        try:
            with self.conn:
                cur = self.conn.cursor()
                query = """
                INSERT INTO {table} (created_at, module, qualname, arg_types, return_type, yield_type)
                VALUES (%s, %s, %s, %s, %s, %s)""".format(table=self.table)
                cur.executemany(query, values)
        except Exception as e:
            logger.exception(str(e))


class MysqlStoreMonkeyTypeConfig(Config):
    def __init__(self, connection_string: str, table: str = DEFAULT_TABLE,
                 sample_rate: Optional[int] = None,
                 code_filter: Optional[CodeFilter] = None,
                 type_rewriter: Optional[TypeRewriter] = None):
        self.connection_string = connection_string
        self.table = table
        self._trace_store = MySQLStore(self.connection_string, self.table)
        self._sample_rate = sample_rate
        self._code_filter = code_filter if code_filter else default_code_filter
        self._type_rewriter = type_rewriter if type_rewriter else DEFAULT_REWRITER

    def trace_store(self) -> CallTraceStore:
        return self._trace_store

    def code_filter(self) -> CodeFilter:
        return self._code_filter

    def type_rewriter(self) -> TypeRewriter:
        return self._type_rewriter

    def sample_rate(self) -> Optional[int]:
        return self._sample_rate
