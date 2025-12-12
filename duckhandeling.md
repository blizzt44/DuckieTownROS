In terminal:

1. 
```bash
ssh 
```

2.  ```dts devel build -f -H ![duck_name]```

3.  ```dts devel run -H ![duck_name] -L ![launchfile]```



If docker container is on:

In new terminal:

1. ```bash ssh duckie@![duck_name].local```
            Password: quackquack

2. ```docker ps```
        Find the running container 

3. ```docker stop ![running_container]```

4.  ```logout```


Fleet discover:
You need to be on the same network for this to work and if you are on a hotspot have it running before the bots are started. 

In terminal:

1.  ```dts fleet discover```


Change WIFI on bots:

1.  ```cd /etc```

2.  ```sudo nano wpa_supplicant.conf```

3. change ssid to WIFI name

4. change psk to WIFI password

NOTE: Do not have space or any other weird symbols in WIFI name

5. To get out of the page press ctrl+s and then ctrl+x

6. Reboot system by  executing:  ```systemctl reboot```