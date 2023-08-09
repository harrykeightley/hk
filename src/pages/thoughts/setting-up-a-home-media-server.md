---
layout: ../../layouts/PostLayout.astro
title: "Setting up a Home Media Server"
subtitle: "And other voyages across the high seas"
date: "2023-08-08"
hidden: false
---

Last month, my relationship with netflix officially ended. 

![netflix-booting-me-off](/homeserver/netflix.png)

More precisely, my _family's_ relationship with netflix (off which I was
comfortably mooching) changed, ending 8 years of a great thing. Towards the end,
I'll admit I was becoming less satisfied with the extents of netflix's library,
and a sort of fatigue was setting in where I'd have to ping-pong between
different streaming platforms to find the titles I wanted. If 
this sounds like a retrospective "Fine, I never liked you anyway", I'll admit,
you're right; but nonetheless, this was the final kick I needed to start looking
into some more sustainable alternatives to streaming services as a whole.

In this article, I'll go through the steps I took in setting up my home media 
server, and give solutions to the roadblocks I faced.

## Table of Contents
1. [Overview](#1-overview)
    1. [Disclaimer](#11-disclaimer)
    2. [Value Proposition](#12-value-proposition)
    3. [Requirements](#13-requirements)
    4. [The tech stack](#14-tech-stack)
2. [Prepping the Hardware](#2-hardware)
    1. [Dell Optiplex BIOS witchcraft](#21-preparing-the-optiplex)
    2. [Preparing and Installing Linux](#22-preparing-and-installing-linux)
    3. [Router Configuration](#23-router-configuration)
3. [Software](#3-software)
    1. [Why Docker?](#31-why-docker)
    2. [Installing Docker](#32-installing-docker)
    3. [The Best Docker Setup](#33-the-best-docker-setup)
    4. [My docker compose file](#34-my-docker-compose-file)
    5. [Running the docker services](#35-running-the-docker-services)
    6. [Service Configuration](#36-configuring-the-services)
    7. [Jellyfin Clients, and building for Samsung TV OS](#37-jellyfin-clients)
4. [Next Steps](#4-next-steps)


## 1. Overview
### 1.1 Disclaimer
[Piracy is a crime](https://www.youtube.com/watch?v=HmZm8vNHBSU). <small>Hilariously,
the producers of that ad didn't have the rights to the music they used.</small> 

Throughout this article, the terms _media_ and _media library_ will henceforth refer to the legal downloading 
and storage of linux .iso files. This is to make it absolutely clear, that media does 
_not_ refer to movies, tv series, and the like.

### 1.2 Value Proposition
![trade offer](/homeserver/tradeoffer.jpg)
**You receive:**  
- Unbounded access to any media your heart desires.
- You can view this media through any client on your local network, unaffected by
  ISP network maintenance (which happens more than I'd like in Australia.)
- No subscriptions or the fatigue that comes with them.

**You offer:**
- One day of configuration
- The cost of a basic server rig. I picked up a [Dell Optiplex 7040](https://www.amazon.com.au/dp/B0BX3PVQ6M)
  with 8GB DDR4 RAM and 1TB Storage for $150 AUD.
- The increased cost of electricity.

### 1.3 Requirements
For this guide, basic competency with \*nix sytems and the commandline is 
assumed. It is likely you will encounter your own unique set of roadblocks 
during installation, and you must be willing to fix these on your own.

### 1.4 Tech Stack
- [Fedora 38](https://fedoraproject.org/): A solid, linux operating system.
    - [Docker](https://www.docker.com/): Run containerized applications on your OS. 
        - [Jellyfin](https://jellyfin.org/): Media server/client for your local network.
        - [qbittorrent](https://www.qbittorrent.org/download): Torrent client for downloading media files.
        - [The Starr stack](https://wiki.servarr.com/) (\*arr): Sources and coordinates torrents with qbittorrent.

Among alternatives, the main idealogical factor here was choosing open source software. 
You could, for example, skip the linux installation and use windows 10 for your 
operating system. In this specific example I'd argue the effect would be like sucking soup 
through a paper straw. 

I should note that [Plex](https://www.plex.tv/en-au/) is touted as a common 
alternative to Jellyfin. Plex has prebuilt clients for a large number of devices,
at the downside that you have to sign up for an account with them, and it's not 
OSS. That was a no from me. 
 
## 2. Hardware
In this section, we'll reformat the optiplex, install linux on it, and then 
assign it a static local ip adress from the router.

### 2.1 Preparing the Optiplex
It's BIOS time baby. Boot that machine up and spam `F11` and `F12`, because I can 
never remember which one's which. We want to get to the BIOS options menu, so 
we can:
- a: Make sure the Optiplex accepts the live linux image.
- b: Configure its behaviour to reboot after power loss.
- c: Tell the computer to never sleep.
- d: Perform a data wipe to silence the paranoid, neurotic demon on your shoulder.

A key resource for me here was [this video](https://youtu.be/n8VwTYU0Mec?t=92) 
by Phillip Yip, showing from scratch how he installs Ubuntu on the same machine. 
He covers points, _a_ and _d_ above. The other steps can be achieved from 
the _Power Management_ tab in the BIOS settings.

If you've followed these steps so far, you'll likely be seeing this gorgeous
interface:
![Wiping the optiplex](/public/homeserver/wiping.png)

Do not, I repeat, **do not** believe the lies of the blue progress bar. I intently watched 
it fill up, only for it to start over again. If you don't have an NVME drive, like me, 
this step can take a couple hours; so in the meantime, let's get Fedora.

### 2.2 Preparing and installing linux.
The most important thing I can do at this stage is warn you not to follow in my
footsteps. 

> **The Dell Optiplex will only see/boot from USB 3.0 Flash Drives!!**

I initially misread this and thought it meant to make sure to _plug the usb into_
a USB 3.0 slot on the back of the machine. Consequently, I wasted ~4 hours scratching
my head and having heartfelt conversations with the machine, begging it to work. 

Now that's out of the way, [download and flash Fedora](https://docs.fedoraproject.org/en-US/quick-docs/creating-and-using-a-live-installation-image/)
to your usb. The second time, I used Fedora Media Writer to do this 
from my mac, and would strongly recommend this. You could also use `dd`, or rufus, 
if these are available to you.

After you're done, here are some ideas for fun tasks to occupy you instead of 
watching that blue progress bar:
- Learn a foreign language.
- Read TAOCP in entirety. 
- Take up the nose flute.

Finally, insert the USB, reboot the computer, and boot from the USB. 

Go through the comfy graphical installation process for Fedora.
The only thing of note here was that I deleted all existing partitions and let
the installer automatically do the allocations, but you do you. 
When done, remove that usb and reboot from your new OS.

### 2.3 Router Configuration
Here the most important step is to give your new machine a static ip address, or 
else you might one day wakeup with none of your services pointing to the 
right places. First on linux, bring up a terminal and type:

`ifconfig -a`

From the results, [find your local ip](https://tecadmin.net/check-ip-address-on-linux/).

The next steps change drastically based on your router, but:
1. Open up your router settings in a browser.
2. Find your way to the DHCP settings.
3. Find the MAC address associated with your machine's local ip address.
4. Make that binding static.

As an additional step, if you can, I'd set your upstream DNS to not 
point to your ISP's servers. I just tried to do this with a Telstra router, and 
I was absolutely shocked that they lock this option down. If this is the case 
with you as well, I'd look up how to just change the DNS server for the fedora 
machine instead of the entire network.

Some common DNS options here:
1. Google DNS - `8.8.8.8, 8.8.4.4`
2. CloudFlare DNS - `1.1.1.1, 1.0.0.1`

## 3. Software
Now that we have our machine up and running, things get a little more 
interesting. We're going to set up a series of docker containers with
`docker-compose`, which are going to communicate with eachother via the local 
network, download media from the web, and store and organise files on disk.

Similar to the rest of the guide, I won't be providing step by 
step instructions, and will instead link material which explains how to do 
everything in much better detail than I can muster in a brief article.

### 3.1 Why docker?
You can absolutely install each of these programs manually instead of through 
containers, so why use docker?

I'd argue that the main points here are security and ease of use. Using 
containers, we can isolate each application from the rest of the computer, 
and eachother. We can give each application least responsibility by 
only allowing access to the directories that we choose them to. In effect, 
we drastically reduce the possibilities of what can go wrong in our system.

The other point is that docker makes the composing and maintenance of these 
applications _incredibly easy_. Want an entirely new application to interop with 
the rest? Just add a few lines to your docker-compose file and restart.
A nice view of your processes? `docker stats`.
I also want to configure only as much as I need for a given result, 
and docker allows me to do just that. 

### 3.2 Installing Docker
The only links you need for this step are [here](https://docs.docker.com/engine/install/fedora/) and
[here](https://docs.docker.com/engine/install/linux-postinstall/).

By the end of the installation process, you should have:
- Docker and docker compose installed. 
- A new `docker` group, which `$USER` is added to. This allows you to run docker 
commands without `sudo`.
- The docker service should start automatically on boot with systemd.

### 3.3 The Best Docker setup.
Here I think you should spend a bit of time reading [this](https://wiki.servarr.com/docker-guide)
amazing resource from [wiki.servarr.com](https://wiki.servarr.com/). This wiki 
has a tonne of useful configuration and troubleshooting guides for all of the 
services we're about to set up, so I'd bookmark and come back to it after you've 
read that initial link. The other really helpful resource at this stage is 
[trash guides](https://trash-guides.info/).

Based off the listed guides, here is the setup I ended up using:
1. Created a new user group (`media`) for all the applications.
2. Created new users for each of the applications, and added them to the `media`
    group. (Added $USER as well)
3. Created my root data folder at `/data`. 
4. Gave the data folder `root:media` ownership with `chown`.
5. Changed folder permissions as per the guides with `chmod`.
6. Inside the `/data` folder, used a structure very similar to [this](https://trash-guides.info/Hardlinks/How-to-setup-for/Docker/),
    but with an extra folder: `/data/config` for application configuration files.

It goes without saying, but I will say it anyway- the directory structure I
used is necessary for my provided docker compose file to work. Don't @ me if you 
try to use it with a different setup and it bites you in the ass.

### 3.4 My docker compose file.
To really see what I mean by how easy it was to use all these applications 
together- take a look at how small [my docker compose](/public/homeserver/docker-compose.yaml) is:


<details>
    <summary>Click to expand my <code>docker-compose.yaml</code>.</summary>

```yaml
version: "3.7"

services:
    Sonarr:
        container_name: Sonarr
        restart: unless-stopped
        image: cr.hotio.dev/hotio/sonarr
        ports:
            - "8989:8989"
        volumes:
            - /data/config/sonarr:/config
            - /data:/data
        environment:
            - PUID=1111 # Application user id setup in previous step
            - PGID=1002 # Media group id
            - UMASK=002
            - TZ=Australia/Brisbane # Obviously replace this.

    Radarr:
        container_name: radarr
        restart: unless-stopped
        image: cr.hotio.dev/hotio/radarr
        ports: 
            - "7878:7878"
        volumes:
            - /data/config/radarr:/config
            - /data:/data
        environment:
            - PUID=1112
            - PGID=1002
            - UMASK=002
            - TZ=Australia/Brisbane

    Prowlarr:
        container_name: prowlarr
        restart: unless-stopped
        image: cr.hotio.dev/hotio/prowlarr
        ports:
            - "9696:9696"
        volumes:
            - /data/config/prowlarr:/config
        environment:
            - PUID=1113
            - PGID=1002
            - UMASK=002
            - TZ=Australia/Brisbane

    Jellyfin:
        container_name: jellyfin
        restart: unless-stopped
        image: cr.hotio.dev/hotio/jellyfin
        ports:
            - "8096:8096"
        volumes:
            - /data/config/jellyfin:/config
            - /data/media:/data/media
        environment:
            - PUID=1114
            - PGID=1002
            - UMASK=002
            - TZ=Australia/Brisbane

    QBitTorrent:
        container_name: qbittorrent
        restart: unless-stopped
        image: cr.hotio.dev/hotio/qbittorrent
        ports: 
            - "8080:8080"
        volumes:
            - /data/config/qbittorrent:/config
            - /data/torrents:/data/torrents
        environment:
            - PUID=1115
            - PGID=1002
            - UMASK=002
            - TZ=Australia/Brisbane
```
</details>

### 3.5 Running the docker services
Ready for the magic? Navigate to wherever you made that `docker-compose.yaml`
file, and enter:

`docker compose up -d`

![running-docker-services](/public/homeserver/itsalive.png)
It's alive! Also, whenever your computer restarts, these services should as well.

### 3.6 Configuring the services
Here's where we return to the servarr wiki and trash guides. We need to do some 
basic setup for each of the services we've just started. 

To access any of these applications, go to the local ip address you found in [step 2.4](),
suffixed with the application port, e.g. if your local ip was `192.168.0.1` and 
you wanted to access Prowlarr, you would open a web browser and go to 
`192.168.0.1:9696`, since in the docker compose file we set 9696 to be Prowlarr's 
port.

Each of the services (apart from jellyfin) has a corresponding set of pages 
for configuration on [servarr](https://wiki.servarr.com) or in 
[trash-guides](https://trash-guides.info/), that you should follow.

As for recommended order, I would go:
1. qbittorrent: [trash-guides link](https://trash-guides.info/Downloaders/qBittorrent/Basic-Setup/)
2. prowlarr: [servarr quick-start](https://wiki.servarr.com/prowlarr/quick-start-guide)
3. sonarr: [servarr quick-start](https://wiki.servarr.com/sonarr/quick-start-guide)
4. radarr: [servarr quick-start](https://wiki.servarr.com/radarr/quick-start-guide)
5. jellyfin: I couldn't find links in servarr or trash-guides. It's a pretty 
    chill setup, so if needed, I'd go through with 
    a youtube video like [this](https://www.youtube.com/watch?v=XzwFMqp_b_c), 
    but ignoring plugins at this stage until you're familiar with jellyfin.

At this stage, you should be completely ready to go! The servarr wiki has 
guides on how to use the individual services. Welcome aboard me-hearty!

### 3.7 Jellyfin clients
To actually watch the media you've just setup all these processes for, you can 
either go to the jellyfin server ip on any device in your local network, or 
find a client for the specific device you're on. I find for my computers I just 
visit the ip addresss, but for TV, I wanted a native client, so I had some more 
hacking to do.

Enter, [the godsend](https://github.com/Georift/install-jellyfin-tizen). This 
man really provided a single docker image which, given the ip of your (samsung) tv, 
does the entire build and installation process! Amazing.

I had one significant roadblock here, which was that I needed to increase the 
number of files allowed to spawn from my docker container, by running a slightly 
different version of the supplied command:

`docker run --rm --ulimit nofile=<bigint>:<bigint> georift/install-jellyfin-tizen <samsung tv ip>`

Setting bigint to bigger and bigger values until it worked. I can't remember 
what I used at this time. Good luck.

## 4. Next Steps
Enjoy yourself a little bit. You deserve it. To improve this setup, the two 
places I'd suggest are:

1. Add a [pihole](https://pi-hole.net/) into the mix. In addition to blocking 
ads for your whole network, you can assign local hostnames to ip addresses. For 
example, I have my server setup to be at home.server on the local network.
2. Along the same lines, a small quality of life fix could be to create a 
reverse proxy, which you could use to point addresses like jellyfin.server to 
your jellyfin service, instead of having to remember ports and ip addresses.
3. If you feel brave, look into seting up a VPN _à la [wireguard](https://www.wireguard.com/)_,
which will give you access to all your media from outside the local network.

Above all, I hope you enjoy the fruits of your labour.



