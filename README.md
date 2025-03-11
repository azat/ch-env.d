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

### Additional scripts

- [`clog.py`](scripts/clog.py) - highlight ClickHouse logs in the same way as ClickHouse does
- [`kafkalog.py`](scripts/kafkalog.py) - highlight Kafka logs
- [`difffolded.pl`](scripts/difffolded.pl) - version of well known `difffolded.pl` that accept `\r`
- And [others](scripts)

### Updating

From the `ch-env` repository:

```
git subtree --prefix=ch-env.d pull ../ch-env.d main
```
