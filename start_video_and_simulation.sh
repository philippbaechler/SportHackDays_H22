ssh -i .ssh/hslukey.sec ubuntu@86.119.35.55 './SportHackDays_H22/start_simulation.sh'

vlc --zoom=0.5 --start-time=0 --stop-time=300 --play-and-exit ~/ownCloud/SHD_Sport_Hackdays/output.mp4

ssh -i .ssh/hslukey.sec ubuntu@86.119.35.55 './SportHackDays_H22/stop_simulation.sh'
