#!/bin/bash

# cd to the Django project dir this script lives in; the secrets file and
# venv are expected two levels up (alongside the repo, outside it)
cd "$(dirname "$(readlink -f "$0")")"
tmux new -d -s hordor_server /bin/bash
tmux send-keys -t hordor_server "source ../../hordor_secrets.env" Enter
tmux send-keys -t hordor_server "source ../../venv/bin/activate" Enter
tmux send-keys -t hordor_server "python manage.py runserver 0.0.0.0:8000" Enter
