#!/bin/sh
set -e

REALPATH=$(realpath $0)
REALDIR=$(dirname $REALPATH)
cd $REALDIR
export PYTHONPATH=$PYTHONPATH:$(dirname $REALDIR)

# Wrap ourselves in a new dbus session if no already done so
if [ "$1" != "--internal" ]
then
	/usr/bin/dbus-run-session -- $REALPATH --internal
	exit $?
fi

teardown()
{
	echo "# --- teardown ---"
	kill $SERVICE_PID
	echo "#  stopped ${SERVICE_PID}"
}

setup()
{
	echo "# --- setup ---"
	../pass_secret_service.py &
	SERVICE_PID=$!
	echo "#  Started ${SERVICE_PID}"
	trap teardown EXIT
}

setup

# --- run tests ---

for TEST in test_*.py
do
	echo "# --- ${TEST} ---"
	./$TEST || echo "# !!! FAILED !!!"
done
