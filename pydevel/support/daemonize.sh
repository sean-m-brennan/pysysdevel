#!/bin/bash
## Daemonization engine: requires a script path
##   input:  a short application name and a script path
##   output: a unique identifier for the lock and log files

# redirect tty fds to /dev/null
redirect-std() {
    log_to=/dev/null
    if [ $# -eq 1 ]; then
	log_to=$1
    fi
    [[ -t 0 ]] && exec </dev/null
    [[ -t 1 ]] && exec >$log_to
    [[ -t 2 ]] && exec 2>$log_to
}
 
# close all non-std* fds
close-fds() {
    eval exec {3..255}\>\&-
}
 
# full daemonization of external command with setsid
daemonize-setsid() {
    APP_NAME=$1
    shift
    uuidkey=`cat /proc/sys/kernel/random/uuid`
    lockfile=/tmp/$APP_NAME.$uuidkey.lock
    logfile=/tmp/$APP_NAME.$uuidkey.log

    (                          # 1. fork
        redirect-std $logfile  # 2. redirect stdin/stdout/stderr before setsid
        cd /                   # 3. ensure cwd isn't a mounted fs
        #umask 0               # 4. umask (leave this to caller)
        close-fds              # 5. close unneeded fds
	echo "$$" > $lockfile  # 6. unique lock file
	echo $uuidkey
        setsid "$@"            # 7. run
	unlink $lockfile       # 8. release lock
    ) &
}
 
# daemonize without setsid, keeps the child in the jobs table
daemonize-job() {
    APP_NAME=$1
    shift
    uuidkey=`cat /proc/sys/kernel/random/uuid`
    lockfile=/tmp/$APP_NAME.$uuidkey.lock
    logfile=/tmp/$APP_NAME.$uuidkey.log

    (                          # 1. fork
        redirect-std $logfile  # 2.1. redirect stdin/stdout/stderr
        trap '' 1 2            # 2.2. guard against HUP and INT (in child)
        cd /                   # 3. ensure cwd isn't a mounted fs
        #umask 0               # 4. umask (leave this to caller)
        close-fds              # 5. close unneeded fds
	echo "$$" > $lockfile  # 6. unique lock file
	echo $uuidkey
        if [[ $(type -t "$1") == file ]]; then
            exec "$@"          # 7. run a script
        else
            "$@"               # 7. run a command or
        fi
	unlink $lockfile       # 8. release lock
    ) &
    disown -h $!               # 2.3. guard against HUP (in parent)
}

# prefer daemonize-setsid method
daemonize() {
    if [ which setsid &> /dev/null ]; then
	daemonize-setsid $@
    else
	daemonize-job $@
    fi
}


##############################

if [ $# -lt 2 ]; then
    echo "Error: daemonizer requires at least an app name and a script to run."
    exit 1
fi

APP_NAME=$1
shift
RUN_SCRIPT=$1
shift

if [ x"$APP_NAME" == x ]; then
    APP_NAME="_"
fi
if [ ! -f "$RUN_SCRIPT" ]; then
    echo "Error: script to daemonize ($RUN_SCRIPT) not present."
    exit 1
fi

daemonize $APP_NAME $RUN_SCRIPT $@
