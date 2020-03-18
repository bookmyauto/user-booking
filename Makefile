pull:
	git pull
update:
	pip3 install -r requirements.txt
server:
	$(info lsof -i:7004 | awk 'FNR > 1 {print $$2}' | xargs sudo kill -9)
	$(info killing already exiting process)
	$(shell lsof -i:7004 | awk 'FNR > 1 {print $$2}' | xargs sudo kill -9)
	$(info starting  process)
	mysqld_safe --skip-grant-tables &
	python3 main.py
