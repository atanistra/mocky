#!/usr/bin/env bash

set -ex

export EXEC_USER_NAME=exec_user

export MOCK_WORKDIR=${MOCK_WORKDIR:-/mock}
export MOCK_RESPONSES_DIR_NAME=${MOCK_RESPONSES_DIR_NAME:-responses}


echo ${MOCK_WORKDIR}/${MOCK_RESPONSES_DIR_NAME}

function add_exec_user() {
    if [ -z "${EXEC_USER_ID}" ]
    then
        EXEC_USER_ID=0
    fi

    if [ ${EXEC_USER_ID} == 0 ]
    then
        useradd -m -o -g 0 -u ${EXEC_USER_ID} ${EXEC_USER_NAME}
    else
        useradd -m -o -u ${EXEC_USER_ID} ${EXEC_USER_NAME}
    fi
}

#id -u exec_user &> /dev/null || add_exec_user

if [ "${1}" == "mock" ]
then
    su ${EXEC_USER_NAME} -c "mkdir -p ${MOCK_WORKDIR}/${MOCK_RESPONSES_DIR_NAME}"
    su ${EXEC_USER_NAME} -c "python3 /mock.py"
else
    exec "$@"
fi
