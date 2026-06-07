.PHONY: build test deploy restart logs clean

DOMAIN ?= cyberwithtaptue.com
APP_DIR ?= /var/www/cyberwithtaptue
VENV ?= $(APP_DIR)/venv

build:
	$(VENV)/bin/pip install -r $(APP_DIR)/requirements/base.txt
	$(VENV)/bin/python $(APP_DIR)/manage.py collectstatic --noinput --settings=config.settings.production
	$(VENV)/bin/python $(APP_DIR)/manage.py migrate --settings=config.settings.production

test:
	$(VENV)/bin/python $(APP_DIR)/manage.py test \
		apps.accounts.tests \
		apps.blog.tests \
		apps.projects.tests \
		apps.events.tests \
		apps.contact.tests \
		apps.meet_legends.tests \
		apps.search.tests \
		--settings=config.settings.production

deploy: build restart

restart:
	sudo systemctl daemon-reload
	sudo systemctl restart gunicorn
	sudo nginx -t && sudo systemctl reload nginx

logs:
	journalctl -u gunicorn -f

clean:
	sudo rm -rf $(APP_DIR)/staticfiles
