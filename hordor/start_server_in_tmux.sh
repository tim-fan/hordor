#!/bin/bash

cd /home/tim/projects/20240505_hodor_small_object_store/hordor/hordor
tmux new -d -s hordor_server /bin/bash
tmux send-keys -t hordor_server "source ../../venv/bin/activate" Enter
tmux send-keys -t hordor_server "python manage.py runserver 0.0.0.0:8000" Enter
