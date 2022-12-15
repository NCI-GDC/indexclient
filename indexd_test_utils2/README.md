# Indexd Test Utils 2

Many of your repos depends on indexd. So, the integration tests
of them need indexd test utils.
The old indexd test utils are using a running postgres database and spin up
a mock indexd server.
This cause problem when trying to run tests in parallel.
There would be conflicts for postgres data and indexd server.

This new test util is to solve the above problems. It use pytest-postgresql to
run multiple postgres process on different port. And random assign port number
to mock indexd server so multiple indexd server could be used at the same time
on the same dev machine.

The travis tests is updated to 3 jobs:
1. Run indexclient tests with old indexd_test_utils
2. Run indexclient tests with new indexd_test_utils2 in single process.
3. Run indexclient tests with new indexd_test_utils2 with pytest-parallel.
4. Run indexclient tests with new indexd_test_utils2 with pytest-xdist.

## How to Usage

1. We still need to install postgres database.
2. Make sure `pg_config` is exported correctly in command line
3. To use indexd_test_utils2, you will need:
    ```yaml
    pytest<7(required by current version of pytest-postgresql)
    pytest-postgresql
    psycopg>3(probably not needed)
    ```
    note: `psycopg>3` can coexist with `psycopyg2` which is ued by `psqlgraph`.

4. (optional) To run tests in parallel, install `pytest-xdist`. Each test will spin up
a postgres database instance and a indexd server instance. So use half number of cores
of your machine as the number of parallel. For example, if you have a 8 core 16 thread
intel cpu, use `pytest -n 8`.

### Known Issues
#### Several problem has been found on my arm mac, ensure you have the following setting
in your env if you are using arm mac:
```bash
LC_ALL=en_US.UTF-8
LC_CTYPE=en_US.UTF-8
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

#### If you ran into memory problem with postgres when doing multi processing, try to increase following params in your /etc/sysctl.conf
```bash
kern.sysv.shmmax=1610612736
kern.sysv.shmall=393216
kern.sysv.shmmin=1
kern.sysv.shmmni=32
kern.sysv.shmseg=8
kern.maxprocperuid=5332
```
