#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

case "${1:-}" in
    build)
        docker compose build dmap
        ;;
    start)
        docker compose up -d dmap
        ;;
    test)
        if ! docker compose ps --status running --services | grep -qx dmap; then
            printf 'Container dmap is not running. Run: %s start\n' "$0" >&2
            exit 1
        fi
        docker compose exec -T dmap python3 test.py
        ;;
    show)
        if ! docker compose ps --status running --services | grep -qx dmap; then
            printf 'Container dmap is not running. Run: %s start\n' "$0" >&2
            exit 1
        fi
        if command -v xhost >/dev/null 2>&1; then
            xhost +local:docker >/dev/null
            trap 'xhost -local:docker >/dev/null 2>&1 || true' EXIT
        fi
        docker compose exec -T \
            -e DISPLAY="${DISPLAY:-:0}" \
            dmap python3 show_video.py
        ;;
    stop)
        docker compose down
        ;;
    *)
        printf 'Usage: %s {build|start|test|show|stop}\n' "$0" >&2
        exit 2
        ;;
esac
