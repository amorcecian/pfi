if ! whoami &> /dev/null; then
  if [ -w /etc/passwd ]; then
    echo "def:x:$(id -u):0:def user:/src:/bin/bash" >> /etc/passwd
  fi
fi

gunicorn app:app -b 0.0.0.0:8080 --log-level=debug --timeout=120 --workers=2 --threads=2