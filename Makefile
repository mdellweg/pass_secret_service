.PHONY: test

test:
	dbus-run-session -- tests/pass_run_session.sh python3 -m unittest discover -s tests
	python3 -m coverage report

#  vim: set ts=8 sw=2 ft=make noet noro norl cin nosi ai :
