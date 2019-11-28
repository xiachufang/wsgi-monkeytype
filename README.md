# WSGI-MonkeyType

Some [MonkeyType](https://monkeytype.readthedocs.io/en/stable/index.html) utils for wsgi application. Include:
- wsgi middleware
- monkeytype mysql store
- flask extension

## Installation

install wsgi-monkeytype
```bash
pip install wsgi-monkeytype
```

install wsgi-monkeytype with mysql store

```bash
pip install wsgi-monkeytype[mysql]
```


install wsgi-monkeytype with flask integration

```bash
pip install wsgi-monkeytype[flask]
```

## Usage
### wsgi middleware

```python
from wsgi_monkeytype import MonkeyTypeWsgiMiddleware
from monkeytype.config import DefaultConfig
config = DefaultConfig()

wsgi_app = ...
wsgi_app = MonkeyTypeWsgiMiddleware(wsgi_app, config)
```

### flask extension
```python
from flask import Flask
from wsgi_monkeytype.flask import MonkeyType
from monkeytype.config import DefaultConfig


# use sqlite store
config = DefaultConfig()

app = Flask()
MonkeyType(config).init_app(app)
```

### monkeytype mysql store
```python
from wsgi_monkeytype.mysql_store import MysqlStoreMonkeyTypeConfig
config = MysqlStoreMonkeyTypeConfig("mysql://user:password@host:port/db", sample_rate=1)
```

## License
BSD
