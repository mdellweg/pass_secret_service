test:
	dbus-run-session -- tests/pass_run_session.sh python3 -m unittest discover -s tests
	python3 -m coverage report
