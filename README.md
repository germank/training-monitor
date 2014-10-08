# Training Monitor

This application permits to plot data streamed through the network to monitor the status of some dynamical system


##Requirements
 * Python > 2.7 (<3?)
 * cherrypy
 * wxpython
 * pyyaml
 * signalslot

## Usage example

`python main.py example.yml`

Go to your browser and open the following urls:

1. [http://localhost:3333/test1/?x=1&y=1](http://localhost:3333/test1/?x=1&y=1)
2. [http://localhost:3333/test1/?x=2&y=2](http://localhost:3333/test1/?x=2&y=2)
3. [http://localhost:3333/test1/?x=3&y=6](http://localhost:3333/test1/?x=3&y=6)
1. [http://localhost:3333/test2/?x=1&y=1](http://localhost:3333/test2/?x=1&y=1)
2. [http://localhost:3333/test2/?x=2&y=4](http://localhost:3333/test2/?x=2&y=4)
3. [http://localhost:3333/test2/?x=3&y=8](http://localhost:3333/test2/?x=3&y=8)
