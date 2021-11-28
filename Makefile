dockerComposeProjectName = "photoneo-test"
vagrantAnsibleInventoryFile = "src/ansible/inventory/vagrantHosts"

dockerComposeInstance:
	docker-compose --project-name="$(dockerComposeProjectName)" -f src/docker-compose/docker-compose.yml up -d

dockerComposeStopInstance:
	docker-compose --project-name="$(dockerComposeProjectName)" -f src/docker-compose/docker-compose.yml down

dockerComposeRemoveInstance:
	docker-compose --project-name="$(dockerComposeProjectName)" -f src/docker-compose/docker-compose.yml down -v --time=0

ansibleRunLocal:
	ansible-playbook \
		--ask-become-pass \
		${VERBOSITY:-} \
	 	src/ansible/local-playbook.yml

ansibleRun:
	 ansible-playbook \
 		--inventory src/ansible/inventory/servers.yaml \
 		-u vagrant \
 		--inventory-file src/ansible/inventory/vagrantHosts \
 		--private-key src/vagrant/.vagrant/machines/default/virtualbox/private_key \
 		${VERBOSITY:-} \
	 	src/ansible/playbook.yml


pythonInstallPackages:
	cd src/python && ( \
		python3 -m venv venv; \
       	. ./venv/bin/activate; \
       	pip install -r requirements.txt; \
       	deactivate; \
    )

pythonRunDatabaseScriptDump:
	make -s pythonInstallPackages
	mkdir -p ./workdir
	/usr/bin/python3 ./src/python/dump-database.py --database-host="$(shell make -s vagrantHostIp)" --output-file=./workdir/db-dump.sql.zip

pythonRunDatabasePgDump:
	make -s pythonInstallPackages
	@cd src/vagrant && vagrant ssh -c "cd /vagrant/python && python3 pg_dump.py --action=dump" 2>/dev/null

pythonRunDatabasePgRestore:
	make -s pythonInstallPackages
	@cd src/vagrant && vagrant ssh -c "cd /vagrant/python && python3 pg_dump.py --action=restore" 2>/dev/null


pythonRunCreatePage:
	make -s pythonInstallPackages
	cd src/python && /usr/bin/python3 ./create-wiki-page.py --api-endpoint-url="http://$(shell make -s vagrantHostIp)/graphql"

vagrantHostIp:
	@cd src/vagrant && vagrant ssh -c "hostname -I | cut -d' ' -f2" 2>/dev/null

vagrantStartHost:
	cd src/vagrant && vagrant up
	make -s vagrantCreateAnsibleInventoryIniFile

vagrantStopHost:
	cd src/vagrant && vagrant halt

vagrantRemoveHost:
	cd src/vagrant && vagrant destroy

vagrantAttachTerminalToHost:
	cd src/vagrant && vagrant ssh

vagrantCreateAnsibleInventoryIniFile:
	echo "[vagrantHosts]" > "${vagrantAnsibleInventoryFile}"
	echo "$(shell make -s vagrantHostIp)" >> "${vagrantAnsibleInventoryFile}"