FROM wordpress:latest


RUN apt-get update && apt-get install -y wget unzip


RUN wget https://fa.wordpress.org/latest-fa_IR.zip \
    && unzip latest-fa_IR.zip -d /tmp \
    && cp -r /tmp/wordpress/* /var/www/html/ \
    && rm -rf /tmp/wordpress latest-fa_IR.zip \

COPY wp-config.php /var/www/html/

CMD ["apache2-foreground"]