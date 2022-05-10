PROJECT_PATH=/home/ec2-user/realTimeStock
PROJECT_APP=$PROJECT_PATH/app.py
PREVIOUS_PID=$(pgrep -fl realTimeStock)

# 기존 실행되는 백그라운드 프로세스 종료.

if ! [ -z "$PREVIOUS_PID" ]; then
  kill -15  "$PREVIOUS_PID"
  sleep 5
fi

chmod +x "$PREVIOUS_PID"

pip3 install -r requirements.txt
nohup python3 $PROJECT_APP > $PROJECT_PATH/log.out 2>&1 &
