FROM php:8.3-cli-alpine

RUN apk add --no-cache \
    postgresql-dev \
    linux-headers \
    && docker-php-ext-install pdo_pgsql sockets

WORKDIR /var/www/html

COPY . .

EXPOSE 8000

CMD ["php", "-S", "0.0.0.0:8000", "index.php"]
