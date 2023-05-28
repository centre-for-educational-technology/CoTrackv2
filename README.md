# CoTrack 🏆 Best Demo Award at LAK'23 Conference, TX, USA
![image](https://user-images.githubusercontent.com/21138354/148179967-050475f8-87e6-4e70-bef3-dd769e160848.png)
[CoTrack](https://www.cotrack.website/) is a web-based tool for conducting collaborative activities in the classroom. It support remote as well as physical settings.
The tool is being developed as part of my research on building collaboration quality models using machine learning. 

## CoTrack demo
The tool has been presented in the CrossMMLA 2020 workshop held at Learning Analytics and Knowledge Conference, LAK'20 and LAK'23.
> Pankaj Chejara, Luis P. Prieto, Adolfo Ruiz-Calleja, María Jesús Rodríguez-Triana, Shashi Kant Shankar, Reet Kasepalu: CoTrack2: A Tool to Track Collaboration Across Physical and Digital Spaces with Real Time Activity Visualization. CrossMMLA@LAK'21. Companion Proceedings 11th International Conference on Learning Analytics and Knowledge, 2021. (Demo paper).

> Pankaj Chejara, Reet Kasepalu, Luis P. Prieto, Adolfo Ruiz-Calleja, María Jesús Rodríguez-Triana, : CoTrack: A Multimodal Learning Analytics tool to guide teachers during collaborative learning activities with intervention suggestions in classroom. LAK'23. Companion Proceedings 13th International Conference on Learning Analytics and Knowledge, 2023. (Demo paper).

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/IOH4S2doZTA/0.jpg)](https://youtu.be/blyln4v5dCQ)

## Features
* Custom activity design

  CoTrack allows teachers/researchers to cusomize the group activity and data recording. For example, CoTrack supports     
  three different types of group activities: first, which only involves use of collaborative text editor; second, which 
  only involves use of audio/video communication channels; third, which invovles both. The recording can also be 
  ustomized, e.g., record only audio or video.
  
* Multimodal data collection

  CoTrack captures following types of data and provides pre-processed features
  
  * *Voice activity detection (VAD):* Data indicating whether someone speaks or not.
  * *Speech to text:* Transcript from audio data using Google speech-to-text api in real time (only supported in chrome
  browser).
  * *Head movement:* Data approximating head movement in 3D with coordinates X,Y,Z (In development).
  * *Body pose:* Data approximating body pose movement using open-source machine learning models for web (In development).
  * *Writing logs:* Log data of participants' writing in collaborative text editor.
  Activity monitoring
 
* CoTracks offers a real-time dashboard (updates every 30 seconds) presenting a social network (who is talking after whom network) and groups' writing activities in terms of number of revisions made.


## Resources
You can check additional resources about the tool [here](https://www.cotrack.website/en-gb/howto/).


## Installation

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



## License
Copyright (c) 2022 Pankaj Chejara

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
