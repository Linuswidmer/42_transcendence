SHELL := bash

dev:
	bash development.sh

do:
	source export_env.sh && python3 manage.py $(filter-out $@,$(MAKECMDGOALS))
%:
	@: