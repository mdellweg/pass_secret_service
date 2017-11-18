projectdir ::= $(realpath .)
relgnupghome ::= tests/.gnupghome
export GNUPGHOME ::= $(projectdir)/$(relgnupghome)
gpg_key_id ::= "8c2a59a7"
relpassstore ::= tests/.test-password-store
export PASSWORD_STORE_DIR ::= $(projectdir)/$(relpassstore)

.PHONY: all test coverage style clean clean-pycache clean-build

all: style test

test: $(relpassstore)
	dbus-run-session -- python3 -m unittest discover -s tests

coverage: $(relpassstore)
	dbus-run-session -- python3 -m coverage run -m unittest discover -s tests
	python3 -m coverage report

style:
	pycodestyle --max-line-length=159 .

$(relgnupghome): tests/test_key.asc tests/test_ownertrust.txt
	@echo "===== Preparing gpg test keys in $(relgnupghome) ====="
	mkdir -m 700 $(relgnupghome)
	gpg --allow-secret-key-import --import tests/test_key.asc
	gpg --import-ownertrust tests/test_ownertrust.txt

$(relpassstore): $(relgnupghome)
	@echo "===== Preparing password store in $(relpassstore) ====="
	pypass init -p $(relpassstore) $(gpg_key_id)

clean:
	$(RM) -r $(relpassstore)
	$(RM) -r $(relgnupghome)

clean-pycache:
	find . -name '__pycache__' -exec $(RM) -r {} +

clean-build:
	$(RM) -r build/
	$(RM) -r dist/
	$(RM) -r *.egg-info

#  vim: set ts=8 sw=2 ft=make noet noro norl cin nosi ai :
