pip3 install -r requirements.txt

PREVIOUS_PID=$(pgrep -fl realTimeStock)

# 기존 실행되는 백그라운드 프로세스 종료.
if ! [ -z "$PREVIOUS_PID" ]; then
  kill -15  "$PREVIOUS_PID"
  sleep 5
fi

nohup python3 app.py > /home/ec2-user/realTimeStock/nohub.out 2>&1 &
