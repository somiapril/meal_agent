from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import load_preferences, parse_items, recommend_meals


def safe_int(value: object, default: int) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


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


class handler(BaseHTTPRequestHandler):
    def send_json(self, payload: dict, status: int = 200) -> None:
        content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Allow", "POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:
        self.send_json({"message": "POST 요청으로 식단 추천을 받을 수 있어요."})

    def do_POST(self) -> None:
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

    def read_json_body(self) -> dict:
        length = safe_int(self.headers.get("Content-Length"), 0)
        if length <= 0:
            return {}
        raw_body = self.rfile.read(length)
        return json.loads(raw_body.decode("utf-8"))
