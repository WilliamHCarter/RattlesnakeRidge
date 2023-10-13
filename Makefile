
.PHONY: requirements.txt
requirements.txt:
	python3 -m pip freeze > requirements.txt

.PHONY: server
server:
	python3 run_server.py
