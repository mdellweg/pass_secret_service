#!/bin/sh
set -e

REALPATH=$(realpath $0)
REALDIR=$(dirname $REALPATH)
export PYTHONPATH=$PYTHONPATH:$(dirname $REALDIR)

teardown()
{
	echo "# --- teardown ---"
	kill $SERVICE_PID
	echo "#  stopped ${SERVICE_PID}"
}

setup()
{
	echo "# --- setup ---"
	python3 -m coverage run $REALDIR/../pass_secret_service.py &
	SERVICE_PID=$!
	echo "#  Started ${SERVICE_PID}"
	trap teardown EXIT
}

setup

# --- run command ---

"$@"
