import os
import platform
import socket
import time

import psutil
from flask import Flask, render_template

app = Flask(__name__)

START_TIME = time.time()
BYTES_TO_MB = 1024 * 1024
BYTES_TO_GB = 1024 ** 3

# Warm up psutil CPU measurement so subsequent non-blocking calls are accurate.
psutil.cpu_percent(interval=None)


def get_stats():
    uptime_seconds = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"

    cpu_percent = psutil.cpu_percent(interval=None)

    mem = psutil.virtual_memory()
    mem_total_mb = mem.total / BYTES_TO_MB
    mem_used_mb = mem.used / BYTES_TO_MB
    mem_percent = mem.percent

    disk = psutil.disk_usage("/")
    disk_total_gb = disk.total / BYTES_TO_GB
    disk_used_gb = disk.used / BYTES_TO_GB
    disk_percent = disk.percent

    net_io = psutil.net_io_counters()

    return {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "uptime": uptime_str,
        "cpu_percent": cpu_percent,
        "cpu_count": psutil.cpu_count(),
        "mem_total_mb": round(mem_total_mb, 1),
        "mem_used_mb": round(mem_used_mb, 1),
        "mem_percent": mem_percent,
        "disk_total_gb": round(disk_total_gb, 1),
        "disk_used_gb": round(disk_used_gb, 1),
        "disk_percent": disk_percent,
        "net_bytes_sent_mb": round(net_io.bytes_sent / BYTES_TO_MB, 2),
        "net_bytes_recv_mb": round(net_io.bytes_recv / BYTES_TO_MB, 2),
    }


@app.route("/")
def index():
    stats = get_stats()
    return render_template("index.html", stats=stats)


@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
