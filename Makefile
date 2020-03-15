pull:
	git pull
update:
	pip3 install -r requirements.txt
server:
	lsof -i:7004 | awk '{print $2}' | xargs sudo kill -9
	mysqld_safe --skip-grant-tables &
	python3 main.py