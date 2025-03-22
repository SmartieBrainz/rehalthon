<VirtualHost *:80>
    ServerName eduthon.sa
    ServerAlias www.eduthon.sa
    ServerAdmin admin@eduthon.sa
    DocumentRoot /home/eduthon/eduthon_app

    WSGIDaemonProcess eduthon python-path=/home/eduthon/eduthon_app:/home/eduthon/eduthon_app/venv/lib/python3.x/site-packages
    WSGIProcessGroup eduthon
    WSGIScriptAlias / /home/eduthon/eduthon_app/eduthon.wsgi

    <Directory /home/eduthon/eduthon_app>
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>