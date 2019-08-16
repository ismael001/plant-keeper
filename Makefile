-include .env

up-raspap:
	# install RaspAP to create Wifi acces point for Node-Devices
	wget -q https://git.io/voEUQ -O /tmp/raspap && bash /tmp/raspap

up-pk-api-gateway: plant_kiper/wsgi.py
	# pipenv run python manage.py runserver 0.0.0.0:80
	pipenv run gunicorn --workers=3 plant_kiper.wsgi

up-pk-dev-ctl: controllers/run.py
	cd controllers && pipenv run python run.py

up-pk-prom-export: prometheus.py
	pipenv run python prometheus.py

up-plant-keeper: up-pk-api-gateway up-pk-dev-ctl up-pk-prom-export

up-prometheus: prometheus.yml
	# download and install Prometheus
	wget https://github.com/prometheus/prometheus/releases/download/v2.12.0-rc.0/prometheus-2.12.0-rc.0.linux-armv7.tar.gz
	tar xf prometheus-2.12.0-rc.0.linux-armv7.tar.gz
	# copy current prometheus configuration
	yes | sudo cp prometheus.yml ../prometheus-2.12.0-rc.0.linux-armv7
	# start prometheus server
	cd .. && cd /prometheus-2.12.0-rc.0.linux-armv7 && ./prometheus --config.file="prometheus.yml"

up-grafana:
	# download and install Granafa
	wget https://dl.grafana.com/oss/release/grafana_6.3.3_armhf.deb
	sudo dpkg -i grafana_6.3.3_armhf.deb
	# ethernet to localport 3000>3000
	sudo iptables -t nat -A PREROUTING -p tcp --dport 3000 -j REDIRECT --to-port 3000

updb: ##@dev
	pipenv run python manage.py makemigrations
	pipenv run python manage.py migrate

create-su: ##@dev
	-pipenv run python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" || echo "Error while creating admin"

runserver-dev:
	pipenv run python manage.py runserver

dj-shell:
	pipenv run python manage.py shell -i ipython


core-unittest: core/tests/test_base_controller.py core/tests/test_base_time_range_controller.py
	cd ${PWD}/core/tests ;\
	pipenv run python test_base_controller.py ;\
	pipenv run python test_base_time_range_controller.py

run-tests: core-unittest