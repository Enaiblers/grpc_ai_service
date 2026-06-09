#!/bin/bash

if [ ! "$(whoami)" == "root" ]; then
    echo "$0"": Need to be root"
    exit 1
fi
if [ -z "$SUDO_USER" ]; then
    echo "$0"": Please run with 'sudo'"
    exit 1
fi
NOSUDO="sudo -E -u $SUDO_USER -H"

echo "Installing dependencies..."

$NOSUDO python3.9 -m pip install grpcio grpcio-health-checking protobuf grpcio-tools

SVCNAME="grpc_ai_model.service"
DST_UNIT1="/etc/systemd/system/$SVCNAME"
ExecStart="/home/$SUDO_USER/microAeye/AI/grpc_ai_service/__main__.py"
User=$USER

if [ ! $1 == "" ]; then 
  ExecStart="$1"
fi
if [ ! $2 == "" ]; then
  User="$2"
fi

if [ ! -f "$DST_UNIT1" ]; then
echo "Creating $DST_UNIT1 service file"
  /bin/cat <<EOF >$DST_UNIT1
[Unit]
Description=grpc AI model service app
[Service]
User=$User
Group=$User
ExecStart=/usr/local/bin/python3.9 $ExecStart
Restart=on-failure
RestartSec=10s
KillMode=process
TimeoutSec=infinity
[Install]
WantedBy=network.target
EOF
systemctl daemon-reload
else
  echo "$DST_UNIT1 already exists"
fi

if ! systemctl is-enabled $SVCNAME; then
  echo "Enabling $SVCNAME"
  systemctl enable $SVCNAME
else
  echo "$SVCNAME already enabled"
fi
systemctl start $SVCNAME