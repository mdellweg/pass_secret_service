#!/bin/sh
set -e

REALPATH=$(realpath $0)
REALDIR=$(dirname $REALPATH)
export PYTHONPATH=$PYTHONPATH:$(dirname $REALDIR)

teardown()
{
  kill $SERVICE_PID || true
  rm -r $PASSWORD_STORE_DIR || true
  rm -r $GNUPGHOME || true
}

setup_gpg()
{
  # prepare gnupg directory
  export GNUPGHOME=$(realpath $REALDIR/../.gnupg)
  gpg --allow-secret-key-import --import $REALDIR/test_key.asc
  gpg --import-ownertrust $REALDIR/test_ownertrust.txt
  export GPG_KEY_ID=8c2a59a7
}

setup_pass()
{
  # prepare test data
  export PASSWORD_STORE_DIR=$(realpath $REALDIR/../.test-password-store)
  pass init $GPG_KEY_ID
  echo "password" | pass insert -e secret_service/default/aaaa
  echo '{"default": "default"}' > $PASSWORD_STORE_DIR/secret_service/.aliases
}

setup()
{
  setup_gpg
  setup_pass
  # run service
  python3 -m coverage run $REALDIR/../pass_secret_service.py --path $PASSWORD_STORE_DIR &
  SERVICE_PID=$!
  trap teardown EXIT
}

setup

"$@"

# vim: set ts=2 sw=2 ft=sh et noro norl cin nosi ai :
