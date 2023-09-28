FROM postgres:16

COPY ./docker-entrypoint-initdb.d/create_questions.py /docker-entrypoint-initdb.d/

LABEL description="This is the Metabase backend"

VOLUME /var/lib/postgresql/data

EXPOSE 1132