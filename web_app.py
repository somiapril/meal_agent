from __future__ import annotations

import json
import mimetypes
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from main import load_preferences, parse_items, recommend_meals


APP_DIR = Path(__file__).resolve().parent
HOST = "127.0.0.1"
DEFAULT_PORT = 8000


def read_text_file(path: Path) -> bytes:
    return path.read_bytes()


def safe_int(value: object, default: int) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def find_open_port(start_port: int = DEFAULT_PORT) -> int:
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex((HOST, port)) != 0:
                return port
        port += 1


def result_to_payload(result: dict) -> dict:
    meal = result["meal"]
    return {
        "name": meal.name,
        "minutes": meal.minutes,
        "difficulty": meal.difficulty,
        "required": sorted(meal.required),
        "optional": sorted(meal.optional),
        "tools": sorted(meal.tools),
        "recipe": meal.recipe,
        "tip": meal.tip,
        "reasons": result["reasons"],
        "warnings": result["warnings"],
        "score": result["score"],
    }


class MealAgentHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")

    def send_bytes(self, content: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, payload: dict, status: int = 200) -> None:
        content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_bytes(content, "application/json; charset=utf-8", status)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.serve_file(APP_DIR / "templates" / "index.html", "text/html; charset=utf-8")
            return

        if parsed.path.startswith("/static/"):
            relative_path = unquote(parsed.path.removeprefix("/static/"))
            file_path = (APP_DIR / "static" / relative_path).resolve()
            static_root = (APP_DIR / "static").resolve()
            if not str(file_path).startswith(str(static_root)) or not file_path.exists():
                self.send_json({"error": "파일을 찾을 수 없어요."}, 404)
                return
            content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
            self.serve_file(file_path, content_type)
            return

        self.send_json({"error": "페이지를 찾을 수 없어요."}, 404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/recommend":
            self.handle_recommend()
            return

        self.send_json({"error": "지원하지 않는 요청이에요."}, 404)

    def serve_file(self, path: Path, content_type: str) -> None:
        try:
            self.send_bytes(read_text_file(path), content_type)
        except FileNotFoundError:
            self.send_json({"error": "파일을 찾을 수 없어요."}, 404)

    def read_json_body(self) -> dict:
        length = safe_int(self.headers.get("Content-Length"), 0)
        if length <= 0:
            return {}
        raw_body = self.rfile.read(length)
        return json.loads(raw_body.decode("utf-8"))

    def handle_recommend(self) -> None:
        try:
            data = self.read_json_body()
        except json.JSONDecodeError:
            self.send_json({"error": "입력값을 읽지 못했어요."}, 400)
            return

        preferences = load_preferences()
        context = {
            "ingredients": parse_items(data.get("ingredients", "")),
            "condition": str(data.get("condition", "")).strip(),
            "environment": str(data.get("environment", "")).strip(),
            "max_minutes": safe_int(data.get("max_minutes"), 20),
            "avoid_items": parse_items(data.get("avoid_items", "")),
            "tools": parse_items(data.get("tools", "")),
            "spice_text": str(data.get("spice_text", "보통")).strip(),
        }

        results = recommend_meals(context, preferences)
        top_results = results[:3]
        payload = {
            "notes": list(dict.fromkeys(top_results[0]["agent_notes"])) if top_results else [],
            "meals": [result_to_payload(result) for result in top_results],
        }

        self.send_json(payload)


def main() -> None:
    port = find_open_port()
    server = ThreadingHTTPServer((HOST, port), MealAgentHandler)
    print("오늘 뭐 먹지 Agent 웹 버전")
    print(f"http://{HOST}:{port}")
    print("종료하려면 Ctrl+C를 누르세요.")
    server.serve_forever()


if __name__ == "__main__":
    main()
