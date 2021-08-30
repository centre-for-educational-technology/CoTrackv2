# Setting up CoTrack Server

CoTrack server requires pre-configured Etherpad server in order to support Etherpad use.

Following steps will show you step by step process on how to set up CoTrack server.

1. Clone CoTrack repository

   ```shell
   git clone https://github.com/pankajchejara23/CoTrackv2
   ```

   The above command will clone the CoTrack repository on your system.

2. Install required libraries on the system.

   Next, you need to install following packages on your systems.

   Install `Python 3.5.2` first on your system.

   Next run following commands to install python packages used by CoTrack

   ```sh
   cd CoTrackv2
   pip install -r requirements.txt
   ```

   

3. Install Etherpad

   You can follow [these instructions](https://www.rosehosting.com/blog/how-to-install-etherpad-on-ubuntu-18-04/) to set up Etherpad server on your server (till step 5). 

   > While creating db in mysql for Etherpad, create an addtional db for CoTrack server as well.

4. Install modules for Apache

   Run following commands to set up Apache server

   ```sh
   sudo apt-get install apache2 libapache2-mod-wsgi
   ```

   ```sh
   a2enmod proxy
   a2enmod proxy_http
   ```

   

5. Configure Apache website

   The following confugration file can be used to configure website in Apache with CoTrack and Etherpad

   ```html
   <IfModule mod_ssl.c>
   <VirtualHost *:443>
       ServerName www.cotrack.website
   
       # SSL configuration
       SSLEngine on
       # If you hold wildcard certificates for your domain the next two lines are not necessary.
       #SSLCertificateChainFile "/etc/ssl/ca_bundle.crt"
   
       WSGIScriptAlias / /home/cotrack/CoTrack-Web-mvps/TrustedUX/wsgi.py
   
       Alias /static /home/cotrack/CoTrack-Web-mvps/static
       Alias /media /home/cotrack/CoTrack-Web-mvps/media
   
       <Directory "/home/cotrack/CoTrack-Web-mvps/TrustedUX">
         <Files wsgi.py>
           Require all granted
         </Files>
       </Directory>
   
       <Directory "/home/cotrack/CoTrack-Web-mvps">
         <Files db.sqlite3>
           Require all granted
         </Files>
       </Directory>
   
   
   
   
       <Directory "/home/cotrack/CoTrack-Web-mvps/static">
         Require all granted
       </Directory>
   
       <Directory "/home/cotrack/CoTrack-Web-mvps/media">
         Require all granted
       </Directory>
   
           SSLCertificateFile /etc/letsencrypt/live/www.cotrack.website/fullchain.pem
   SSLCertificateKeyFile /etc/letsencrypt/live/www.cotrack.website/privkey.pem
   #Include /etc/letsencrypt/options-ssl-apache.conf
   </VirtualHost>
       <VirtualHost *:443>
           ServerName www.etherpad.website
   
           # SSL configuration
           SSLEngine on
           # If you hold wildcard certificates for your domain the next two lines are not necessary.
           #SSLCertificateChainFile "/etc/ssl/etherpad_ca_bundle.crt"
   
           ProxyVia On
           ProxyRequests Off
           ProxyPreserveHost on
   	<Location />
   	  ProxyPass http://localhost:9001/
   	  ProxyPassReverse http://localhost:9001/
   	</Location>
   
   	<Location /socket.io>
   	  RewriteEngine On
   	  RewriteCond %{QUERY_STRING} transport=websocket  [NC]
   	  RewriteRule /(.*) ws://localhost:9001/socket.io/$1 [P,L]
   	  ProxyPass   http://localhost:9001/socket.io
   	  ProxyPassReverse   http://localhost:9001/socket.io
   	</Location>
   	
   
           <Location />
             Order allow,deny
             allow from all
           </Location>
   
   
           <Proxy *>
               Options FollowSymLinks MultiViews
               AllowOverride All
               Order allow,deny
               allow from all
           </Proxy>
                       SSLCertificateFile /etc/letsencrypt/live/www.cotrack.website/fullchain.pem
   SSLCertificateKeyFile /etc/letsencrypt/live/www.cotrack.website/privkey.pem
   #Include /etc/letsencrypt/options-ssl-apache.conf
   </VirtualHost>
       </IfModule>
   ```

   6. Configuring Let's Encrypt for SSL certificate generation.

      Follow [this guide](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-ubuntu-18-04) for generating SSL certificates.



## Configuring Jitsi server

CoTrack uses Jitsi server to offer audio-video communication functionality. Thus, a seperate server needs to be configured for Jitsi.

Follow guide from [this video](https://www.youtube.com/watch?v=jWPod5ubeUM) and [this guide](https://doganbros.com/index.php/jitsi/jitsi-installation-with-jwt-support-on-ubuntu-20-04-lts/).

