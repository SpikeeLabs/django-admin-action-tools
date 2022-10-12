### Local Development Setup

**Local:**
_You can skip this and just use docker if you want_

Install dependence

```bash
# dep
poetry install

# pre-commit
poetry run pre-commit install --install-hook
poetry run pre-commit install --install-hooks --hook-type commit-msg

```

Run **migrations** and create a superuser and run the server

```
poetry run ./tests/manage.py migrate
poetry run ./tests/manage.py createsuperuser

```

Run the docker-compose and **collectstatic**

```bash
docker compose -f "docker/docker-compose.dev.yml" up -d --build localstack selenium
python tests/manage.py collectstatic --no-input
```
Run the Server
```bash
poetry run ./tests/manage.py runserver
```

You should be able to see the test app at `localhost:8000/admin`

**Running tests:**

```sh
poetry run pytest
```

**Coverage:**
```sh
poetry shell
coverage erase && coverage run -m pytest && coverage html && coverage report -m
```


**Debugging**:

There's a environment variable `ADMIN_CONFIRM_DEBUG` which when set to true will print to stdout the messages that are sent to `log`.

The test project already has this set to true.

Example:

```py
from admin_confirm.utils import log

log('Message to send to stdout')
```

**Localstack**:
Localstack is used for integration testing and also in the test project.

To check if localstack is running correctly, go to `http://localhost:4566`
To check if the bucket has been set up correctly, go to `http://localhost:4566/mybucket`
To check if the static files have been set up correctly, go to `http://localhost:4566/mybucket/static/admin/css/base.css`

**Docker:**

Instead of local set-up, you can also use docker. You may have to delete `.python-version` to do this.

Install docker-compose (or Docker Desktop which installs this for you)

```
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d
```

You should now be able to see the app running on `localhost:8000`

If you haven't already done migrations and created a superuser, you'll want to do it here

```
docker-compose -f docker-compose.dev.yml exec web tests/manage.py migrate
docker-compose -f docker-compose.dev.yml exec web tests/manage.py createsuperuser
```

Running tests in docker:

```
docker-compose -f docker-compose.dev.yml exec -T web make test-all
```

The integration tests are set up within docker. I recommend running the integration tests only in docker.

Docker is also set to mirror local folder so that you can edit code/tests and don't have to rebuild to run new code/tests.

Use `docker-compose -f docker-compose.dev.yml up -d --force-recreate` if you need to restart the docker containers. For example when updating the docker-compose.yml file, but if you change `Dockerfile` you have to rebuild.
