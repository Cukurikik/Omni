#!/usr/bin/wish
# OMNI Tcl/Tk Administrative Dashboard

wm title . "OMNI Control Panel"
wm geometry . 300x150

label .lbl -text "OMNI Daemon Status: Unknown" -font {Helvetica 12 bold}
pack .lbl -pady 10

frame .btns
pack .btns -pady 10

button .btns.start -text "Start OMNI" -command {
    .lbl configure -text "OMNI Daemon Status: Running" -foreground green
}
button .btns.stop -text "Stop OMNI" -command {
    .lbl configure -text "OMNI Daemon Status: Stopped" -foreground red
}

pack .btns.start -side left -padx 5
pack .btns.stop -side right -padx 5

button .exit -text "Exit" -command { exit }
pack .exit -pady 10
