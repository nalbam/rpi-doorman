#!/bin/bash

NAME="rpi-doorman"

SHELL_DIR=$(dirname $0)

CMD=${1}

CONFIG=~/.${NAME}
touch ${CONFIG}
. ${CONFIG}

command -v tput > /dev/null || TPUT=false

_echo() {
    if [ -z ${TPUT} ] && [ ! -z $2 ]; then
        echo -e "$(tput setaf $2)$1$(tput sgr0)"
    else
        echo -e "$1"
    fi
}

_read() {
    if [ -z ${TPUT} ]; then
        read -p "$(tput setaf 6)$1$(tput sgr0)" ANSWER
    else
        read -p "$1" ANSWER
    fi
}

_result() {
    _echo "# $@" 4
}

_command() {
    _echo "$ $@" 3
}

_success() {
    _echo "+ $@" 2
    exit 0
}

_error() {
    _echo "- $@" 1
    exit 1
}

_status() {
    PID=$(ps -ef | grep python3 | grep " run[.]py" | head -1 | awk '{print $2}' | xargs)
    if [ "${PID}" != "" ]; then
        _result "${NAME} is running: ${PID}"
    else
        _result "${NAME} is stopped"
    fi
}

_stop() {
    if [ "${PID}" == "" ]; then
        return
    fi

    _command "kill -9 ${PID}"
    kill -9 ${PID}

    _status
}

_start() {
    if [ "${PID}" != "" ]; then
        return
    fi

    pushd ${SHELL_DIR}
    _command "python3 run.py"
    # nohup python3 run.py &
    nohup python3 run.py > /dev/null 2>&1 &
    popd

    _status
}

_config_read() {
    if [ -z ${REMOTE_URL} ]; then
        _read "REMOTE_URL [${REMOTE_URL}]: " "${REMOTE_URL}"
        if [ ! -z ${ANSWER} ]; then
            REMOTE_URL="${ANSWER}"
        fi
    fi
    export REMOTE_URL="${REMOTE_URL}"
}

_config_save() {
    echo "# ${NAME} config" > ${CONFIG}
    echo "export REMOTE_URL=${REMOTE_URL}" >> ${CONFIG}

    cat ${CONFIG}
}

_init() {
    pushd ${SHELL_DIR}
    git pull
    popd
}

# _config_read
# _config_save

case ${CMD} in
    init)
        _init
        ;;
    status)
        _status
        ;;
    start)
        _status
        _start
        ;;
    restart)
        _status
        _stop
        _start
        ;;
    stop)
        _status
        _stop
        ;;
    *)
        _status
        _start
        ;;
esac
