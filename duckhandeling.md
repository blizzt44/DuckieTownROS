# Duckiebot Handeling Guide 
This guide aims to explain the handeling of the duckiebots. 

## Running code on the bots

In terminal:

1. 
```bash
cd DuckieTownROS 
```

2.
  ```bash
dts devel build -f -H ![duck_name]
  ```

3.
  ```bash 
dts devel run -H ![duck_name] -L ![launchfile]
  ```

Find the launch files under launchers in the DuckieTownROS dir. 

## Closing docker container on the bots
If docker container is on:

In new terminal:

1.
 ```bash
ssh duckie@![duck_name].local
 ```
Password: quackquack

2.
```bash
docker ps
```
Find the running container 

3.
 ```bash
docker stop ![running_container]
```

4.
  ```bash
  logout
  ```


## Fleet discover
You need to be on the same network for this to work and if you are on a hotspot have it running before the bots are started. 

In terminal:

1.
  ```bash
dts fleet discover
```

If it worked you should see the bots name and their status. It should be saying ready with a green box.

## Change WIFI on bots

Either connect a keyboard and a screen to it or ssh in to it for this. 

1.
  ```bash
cd /etc
```

2.
  ```bash
sudo nano wpa_supplicant.conf
```

3. Change ssid to WIFI name

4. Change psk to WIFI password

NOTE: Do not have space or any other weird symbols in WIFI name

5. To get out of the page press ctrl+s and then ctrl+x

6. Reboot system by  executing:
```bash
systemctl reboot
```


## LED color guide
We don't know if this guide is accurate but this is what we found that the lights meant. 

* **Blue**: Charging
*  **White**: Booting
* **Red and white**: Running

There is more color and when you think you know what it means add it to the list.  
 