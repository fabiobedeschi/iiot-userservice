FROM postgres:13-alpine

EXPOSE 5432

COPY initdb/ /docker-entrypoint-initdb.d/

CMD ["postgres"]
