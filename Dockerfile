FROM ml_edition

ENV PYTHONPATH=/code
WORKDIR code

COPY . .

RUN pip3 install --upgrade poetry==1.8.3

RUN python3 -m poetry config virtualenvs.create false \
    && python3 -m poetry install --no-interaction --no-ansi --without dev \
    && xecho yes | python3 -m poetry cache clear . --all
