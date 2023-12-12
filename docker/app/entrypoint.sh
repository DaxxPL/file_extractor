#!/bin/sh
set -e

if [ "$1" = 'worker_sync' ]; then
  shift
  exec python -u src/worker_sync/main.py $@
elif [ "$1" = 'worker_extract' ]; then
  shift
  exec python -u src/worker_extract/main.py $@
elif [ "$1" = 'lint' ]; then
    shift
    OPTS=${@:-'.'}
    echo "-- black --" && black --check --diff $OPTS || EXIT=$?
    echo "-- isort --" && isort -c --diff $OPTS || EXIT=$?
    echo "-- flake8 --" && flake8 --max-line-length=88 $OPTS || EXIT=$?
    MYPY_OPTS=${@:-'src/'}
    echo "-- mypy --" && mypy $MYPY_OPTS || EXIT=$?
    exit ${EXIT:-0}
elif [ "$1" = 'fmt' ]; then
    shift
    OPTS=${@:-'.'}
    echo "-- black --" && black $OPTS
    echo "-- isort --" && isort --atomic $OPTS
    exit 0
elif [ "$1" = 'test' ]; then
    shift
    exec pytest
elif [ "$1" = 'init-db' ]; then
    shift
    exec yoyo apply --database=postgresql://$PGSQL_USER:$PGSQL_PASSWORD@$PGSQL_SERVER:$PGSQL_PORT/$PGSQL_DATABASE migrations
fi
