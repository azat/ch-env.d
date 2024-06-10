### ch-env.d

My env for ClickHouse development.
I'm using it with `tmuxinator`.

### Usage

Usually you should put the following into `~/.bashrc` or `~/.profile`:

```bash
# fill .env file and
source toolchain.sh
source completion.sh
source jemalloc.sh
source clickhouse.sh
```
