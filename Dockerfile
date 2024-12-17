# BUILD IMAGE:       docker build --network=host -t storm .
# RUN CONTAINER:     docker run --name storm -p 3000:3000 -p 8000:8000 storm
# STOP CONTAINER:    docker stop storm
# RESUME CONTAINER:  docker start storm

FROM python:3.13.1-alpine3.21 AS base

# Install base dependencies
RUN apk add --update --no-cache bash postgresql nodejs npm \
    && npm install -g pnpm

# Environment variables
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
ENV NODE_ENV="production"
ENV DJANGO_DEBUG="False"
ENV PGSERVICEFILE=/app/storm/.pg_service.conf

WORKDIR /app

# --- First Stage: Install project dependencies ---
FROM base AS deps

# Backend code
ADD storm /app/storm
ADD requirements.txt /app/

# Frontend build output and files
ADD storm-ui/.next /app/storm-ui/.next
ADD storm-ui/public /app/storm-ui/public
ADD storm-ui/package.json storm-ui/pnpm-lock.yaml /app/storm-ui/

# Python and Node dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pnpm install --prefix /app/storm-ui

# --- Final Stage: Run DB, Backend and Frontend servers ---
FROM deps AS final

# Initialize database
USER postgres
RUN mkdir /var/lib/postgresql/data \
    && chmod 0700 /var/lib/postgresql/data \
    && initdb /var/lib/postgresql/data \
    && echo "unix_socket_directories = '/tmp'" >> /var/lib/postgresql/data/postgresql.conf
USER root

# Volume for DB data
VOLUME ["/var/lib/postgresql/data"]

# Expose ports
EXPOSE 8000 3000

# Entry script
ADD ./entrypoint.sh /app/

# Initialize servers
CMD ["sh", "./entrypoint.sh"]
