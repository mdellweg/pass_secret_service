#!/bin/sh
set -e

REALPATH=$(realpath $0)
REALDIR=$(dirname $REALPATH)
export PYTHONPATH=$PYTHONPATH:$(dirname $REALDIR)

teardown()
{
	kill $SERVICE_PID || true
	rm -r $PASSWORD_STORE_DIR || true
}

setup()
{
	# prepare test data
	PASSWORD_STORE_DIR=$(realpath $REALDIR/../.test-password-store)
	PASSWORD_STORE_DIR=$PASSWORD_STORE_DIR pass init $GPG_ID
	echo "password" | PASSWORD_STORE_DIR=$PASSWORD_STORE_DIR pass insert -e secret_service/default/aaaa
	echo '{"default": "default"}' > $PASSWORD_STORE_DIR/secret_service/.aliases

	# run service
	PASSWORD_STORE_DIR=$PASSWORD_STORE_DIR python3 -m coverage run $REALDIR/../pass_secret_service.py --path $PASSWORD_STORE_DIR &
	SERVICE_PID=$!
	trap teardown EXIT
}

setup

"$@"
