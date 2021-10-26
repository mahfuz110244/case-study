# case-study Voting App
Bongo case study

## Installation

- rename `example.env` to `.env` and set the correct configurations
- run `docker-compose up --build`
- run `docker-compose exec app bash`
- run `cd src` in docker container
- run `./manage.py migrate` in docker container to create tables
- run `./manage.py init_group` in docker container to initialize groups for Employee and Manager
- run `./manage.py createsuperuser` in docker container to create a superuser for performing admin task
- run `./manage.py test` in docker container for unit testing
- if everything goes right check the health check url at `http://localhost:8000/api/v1`
- check swagger API documentation at `http://localhost:8000/doc/`
- Employee can vote only one in a day before configure deadline time and result will be published after deadline.
