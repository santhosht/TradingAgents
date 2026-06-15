#!/bin/bash

VENV_PYTHON="/root/sant/app/TradingAgents/.venv/bin/python3"
SCRIPT="/root/sant/app/TradingAgents/analysis/reports_viewer.py"
PIDFILE="/tmp/reports_viewer.pid"
LOGFILE="/tmp/reports_viewer.log"

start() {
    if [ -f "$PIDFILE" ] && kill -0 "$(cat $PIDFILE)" 2>/dev/null; then
        echo "Already running (pid $(cat $PIDFILE))"
        return
    fi
    nohup "$VENV_PYTHON" "$SCRIPT" > "$LOGFILE" 2>&1 &
    echo $! > "$PIDFILE"
    echo "Started (pid $!)"
}

stop() {
    if [ ! -f "$PIDFILE" ]; then
        echo "Not running"
        return
    fi
    kill "$(cat $PIDFILE)" 2>/dev/null && echo "Stopped" || echo "Process not found"
    rm -f "$PIDFILE"
}

case "$1" in
    start)   start ;;
    stop)    stop ;;
    restart) stop; sleep 1; start ;;
    *) echo "Usage: $0 {start|stop|restart}" ;;
esac
