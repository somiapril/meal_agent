from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
PREFERENCES_FILE = APP_DIR / "preferences.json"


@dataclass(frozen=True)
class Meal:
    name: str
    required: set[str]
    optional: set[str]
    tags: set[str]
    minutes: int
    difficulty: str
    tools: set[str]
    recipe: list[str]
    tip: str


MENU_CATALOG = [
    Meal(
        name="계란두부국",
        required={"계란", "두부"},
        optional={"대파", "양파", "밥", "김"},
        tags={"warm", "gentle", "quick", "protein", "one_pot", "low_dishes", "light"},
        minutes=15,
        difficulty="쉬움",
        tools={"냄비"},
        recipe=[
            "냄비에 물을 끓이고 두부를 한입 크기로 넣어요.",
            "간장이나 소금으로 약하게 간을 맞춰요.",
            "계란을 풀어 넣고 1분 정도 더 끓여요.",
            "대파나 김이 있으면 마지막에 올려요.",
        ],
        tip="속이 예민한 날에는 고춧가루 없이 맑게 먹는 쪽이 좋아요.",
    ),
    Meal(
        name="두부계란 김치죽",
        required={"밥", "계란", "두부", "김치"},
        optional={"양파", "대파", "참기름", "김"},
        tags={"warm", "quick", "protein", "one_pot", "low_dishes", "filling", "can_be_mild"},
        minutes=20,
        difficulty="쉬움",
        tools={"냄비"},
        recipe=[
            "김치는 물에 살짝 헹구면 덜 자극적이에요.",
            "냄비에 밥, 물, 김치, 두부를 넣고 끓여요.",
            "밥알이 부드러워지면 계란을 풀어 넣어요.",
            "참기름은 아주 조금만 넣거나 생략해요.",
        ],
        tip="더부룩한 날에는 김치를 헹구고 국물을 묽게 잡으면 부담이 줄어요.",
    ),
    Meal(
        name="김치두부덮밥",
        required={"김치", "두부", "밥"},
        optional={"계란", "양파", "대파", "참기름"},
        tags={"quick", "protein", "one_pan", "filling", "spicy"},
        minutes=15,
        difficulty="쉬움",
        tools={"프라이팬"},
        recipe=[
            "김치와 양파를 작게 썰어 프라이팬에 볶아요.",
            "두부를 넣고 으깨듯이 섞어요.",
            "밥 위에 올리고 계란이 있으면 반숙으로 추가해요.",
        ],
        tip="피곤하지만 든든하게 먹고 싶은 날에 좋아요.",
    ),
    Meal(
        name="계란볶음밥",
        required={"밥", "계란"},
        optional={"양파", "당근", "대파", "김", "햄", "김치"},
        tags={"quick", "one_pan", "filling", "low_dishes"},
        minutes=12,
        difficulty="아주 쉬움",
        tools={"프라이팬"},
        recipe=[
            "프라이팬에 기름을 조금 두르고 계란을 먼저 볶아요.",
            "밥과 다진 채소를 넣고 같이 볶아요.",
            "간장이나 소금으로 간을 맞춰요.",
            "김이 있으면 잘라서 올려요.",
        ],
        tip="설거지를 줄이고 싶을 때 가장 안정적인 선택이에요.",
    ),
    Meal(
        name="참치마요덮밥",
        required={"밥", "참치", "마요네즈"},
        optional={"김", "계란", "오이", "양파"},
        tags={"quick", "no_cook", "filling", "low_dishes", "protein"},
        minutes=8,
        difficulty="아주 쉬움",
        tools={"그릇"},
        recipe=[
            "참치의 기름을 가볍게 빼요.",
            "밥 위에 참치, 마요네즈, 김을 올려요.",
            "양파나 오이가 있으면 잘게 썰어 넣어요.",
            "느끼하면 간장이나 후추를 아주 조금 더해요.",
        ],
        tip="불 쓰기 싫은 날에 좋아요. 속이 불편하면 마요네즈 양을 줄여요.",
    ),
    Meal(
        name="토마토달걀볶음",
        required={"토마토", "계란"},
        optional={"양파", "밥", "치즈"},
        tags={"quick", "one_pan", "light", "protein", "gentle"},
        minutes=12,
        difficulty="쉬움",
        tools={"프라이팬"},
        recipe=[
            "토마토를 큼직하게 썰고 계란은 풀어둬요.",
            "계란을 먼저 부드럽게 익힌 뒤 잠시 빼요.",
            "토마토를 살짝 볶고 계란을 다시 넣어 섞어요.",
            "밥과 같이 먹으면 한 끼가 돼요.",
        ],
        tip="기름을 적게 쓰면 밤에도 부담이 덜해요.",
    ),
    Meal(
        name="된장국밥",
        required={"된장", "밥"},
        optional={"두부", "양파", "애호박", "감자", "대파"},
        tags={"warm", "gentle", "one_pot", "filling", "low_dishes"},
        minutes=20,
        difficulty="쉬움",
        tools={"냄비"},
        recipe=[
            "냄비에 물을 끓이고 된장을 풀어요.",
            "두부나 채소가 있으면 넣고 끓여요.",
            "밥을 넣어 국밥처럼 먹거나 따로 곁들여요.",
        ],
        tip="비 오는 날이나 몸이 으슬으슬한 날에 잘 맞아요.",
    ),
    Meal(
        name="오트밀죽",
        required={"오트밀"},
        optional={"계란", "우유", "두유", "바나나", "견과류"},
        tags={"warm", "gentle", "quick", "light", "low_dishes"},
        minutes=7,
        difficulty="아주 쉬움",
        tools={"냄비", "전자레인지"},
        recipe=[
            "오트밀에 물, 우유, 두유 중 하나를 넣어요.",
            "전자레인지나 냄비로 걸쭉해질 때까지 익혀요.",
            "든든하게 먹고 싶으면 계란을 풀어 넣어요.",
            "달게 먹고 싶으면 바나나를 얹어요.",
        ],
        tip="소화가 예민하거나 늦은 시간에 가볍게 먹기 좋아요.",
    ),
    Meal(
        name="고구마계란 플레이트",
        required={"고구마", "계란"},
        optional={"요거트", "견과류", "샐러드", "치즈"},
        tags={"light", "protein", "quick", "low_dishes", "gentle"},
        minutes=15,
        difficulty="아주 쉬움",
        tools={"냄비", "전자레인지"},
        recipe=[
            "고구마는 전자레인지나 찜기로 익혀요.",
            "계란은 삶거나 스크램블로 만들어요.",
            "요거트나 샐러드가 있으면 곁들여요.",
        ],
        tip="다이어트 중이거나 속을 편하게 두고 싶은 날에 좋아요.",
    ),
    Meal(
        name="닭가슴살 샐러드볼",
        required={"닭가슴살", "채소"},
        optional={"계란", "고구마", "토마토", "오이", "요거트"},
        tags={"light", "protein", "no_cook", "quick"},
        minutes=10,
        difficulty="아주 쉬움",
        tools={"그릇"},
        recipe=[
            "익힌 닭가슴살을 먹기 좋게 찢어요.",
            "채소와 토마토, 오이 등을 그릇에 담아요.",
            "드레싱은 조금만 넣고, 부족하면 계란이나 고구마를 더해요.",
        ],
        tip="운동 후나 가볍게 단백질을 챙기고 싶은 날에 좋아요.",
    ),
    Meal(
        name="간단 비빔국수",
        required={"국수"},
        optional={"계란", "오이", "김치", "양파", "참기름"},
        tags={"quick", "cool", "spicy", "filling"},
        minutes=15,
        difficulty="쉬움",
        tools={"냄비", "그릇"},
        recipe=[
            "국수를 삶아 찬물에 헹궈요.",
            "김치나 오이를 올려 식감을 더해요.",
            "고추장 양념은 컨디션에 따라 적게 넣어요.",
            "계란이 있으면 삶아서 곁들여요.",
        ],
        tip="더운 날에는 좋지만 속이 불편하면 양념을 약하게 해요.",
    ),
    Meal(
        name="라면 반개 계란탕",
        required={"라면", "계란"},
        optional={"대파", "두부", "김", "채소"},
        tags={"warm", "quick", "one_pot", "low_dishes", "spicy", "high_sodium"},
        minutes=8,
        difficulty="아주 쉬움",
        tools={"냄비"},
        recipe=[
            "물을 넉넉히 잡고 라면 스프는 절반만 넣어요.",
            "면도 반만 넣고 두부나 채소가 있으면 추가해요.",
            "마지막에 계란을 풀어 넣어 부드럽게 만들어요.",
        ],
        tip="정말 빠른 선택지지만 붓기나 속 불편함이 있으면 다른 메뉴가 나아요.",
    ),
]


SYNONYMS = {
    "달걀": "계란",
    "에그": "계란",
    "egg": "계란",
    "밥공기": "밥",
    "쌀밥": "밥",
    "현미밥": "밥",
    "햇반": "밥",
    "튜나": "참치",
    "참치캔": "참치",
    "마요": "마요네즈",
    "마요네즈소스": "마요네즈",
    "야채": "채소",
    "상추": "채소",
    "양상추": "채소",
    "샐러드채소": "채소",
    "닭가슴": "닭가슴살",
    "치킨": "닭가슴살",
    "면": "국수",
    "소면": "국수",
    "누들": "국수",
}


TAG_LABELS = {
    "warm": "따뜻한 메뉴",
    "cool": "시원한 메뉴",
    "gentle": "속 편한 메뉴",
    "quick": "빠른 조리",
    "protein": "단백질 보충",
    "one_pot": "냄비 하나",
    "one_pan": "팬 하나",
    "low_dishes": "설거지 적음",
    "light": "가벼운 식사",
    "filling": "든든한 식사",
    "no_cook": "불 사용 거의 없음",
    "spicy": "매콤함",
    "high_sodium": "나트륨 높을 수 있음",
}


def normalize_item(text: str) -> str:
    item = text.strip().lower()
    item = re.sub(r"[^\w가-힣]", "", item)
    return SYNONYMS.get(item, item)


def parse_items(text: str) -> set[str]:
    if not text.strip():
        return set()
    raw_items = re.split(r"[,/·\n]+|\s{2,}", text)
    items: set[str] = set()
    for raw in raw_items:
        parts = raw.split()
        if len(parts) > 1 and "," not in raw:
            items.update(normalize_item(part) for part in parts if normalize_item(part))
        else:
            item = normalize_item(raw)
            if item:
                items.add(item)
    return items


def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    answer = input(f"{prompt}{suffix}: ").strip()
    return answer if answer else (default or "")


def load_preferences() -> dict:
    if not PREFERENCES_FILE.exists():
        return {
            "allergies": [],
            "dislikes": [],
            "favorite_ingredients": [],
            "diet_goal": "",
            "spice_level": "보통",
            "tools": ["냄비", "프라이팬", "전자레인지"],
        }
    try:
        return json.loads(PREFERENCES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_preferences(preferences: dict) -> None:
    PREFERENCES_FILE.write_text(
        json.dumps(preferences, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def edit_preferences() -> None:
    preferences = load_preferences()
    print("\n개인 취향을 저장해둘게요. 그냥 Enter를 누르면 기존 값이 유지돼요.")

    allergies = ask("알레르기 재료", ", ".join(preferences.get("allergies", [])))
    dislikes = ask("싫어하거나 피하고 싶은 재료", ", ".join(preferences.get("dislikes", [])))
    favorites = ask("좋아하는 재료", ", ".join(preferences.get("favorite_ingredients", [])))
    diet_goal = ask("식단 목표 예: 다이어트, 단백질, 속 편한 음식", preferences.get("diet_goal", ""))
    spice_level = ask("매운맛 선호 예: 약하게, 보통, 매운맛 좋아함", preferences.get("spice_level", "보통"))
    tools = ask("사용 가능한 조리도구", ", ".join(preferences.get("tools", [])))

    preferences = {
        "allergies": sorted(parse_items(allergies)),
        "dislikes": sorted(parse_items(dislikes)),
        "favorite_ingredients": sorted(parse_items(favorites)),
        "diet_goal": diet_goal,
        "spice_level": spice_level,
        "tools": sorted(parse_items(tools)),
    }
    save_preferences(preferences)
    print("저장 완료!\n")


def analyze_needs(condition: str, environment: str, max_minutes: int, spice_text: str, preferences: dict) -> tuple[set[str], set[str], list[str]]:
    text = " ".join([condition, environment, spice_text, preferences.get("diet_goal", "")]).lower()
    wanted: set[str] = set()
    avoid_tags: set[str] = set()
    notes: list[str] = []

    if max_minutes <= 15:
        wanted.update({"quick", "low_dishes"})
        notes.append("조리 시간이 짧아서 빠른 메뉴를 우선했어요.")

    if any(word in text for word in ["피곤", "기운", "귀찮", "힘들", "바쁨", "바빠"]):
        wanted.update({"quick", "low_dishes"})
        notes.append("피곤하거나 바쁜 상태라 손이 덜 가는 메뉴가 좋아 보여요.")

    if any(word in text for word in ["속", "소화", "더부룩", "체", "메스꺼", "위", "복통"]):
        wanted.update({"gentle", "warm", "light"})
        avoid_tags.update({"spicy", "high_sodium"})
        notes.append("속이 예민할 수 있어 맵고 짠 메뉴는 낮게 평가했어요.")

    if any(word in text for word in ["비", "추", "겨울", "으슬", "감기", "쌀쌀"]):
        wanted.add("warm")
        notes.append("날씨나 환경상 따뜻한 메뉴에 점수를 더 줬어요.")

    if any(word in text for word in ["덥", "여름", "습", "더위"]):
        wanted.update({"cool", "light"})
        notes.append("더운 환경이라 가볍거나 시원한 메뉴도 고려했어요.")

    if any(word in text for word in ["운동", "헬스", "근력", "단백질"]):
        wanted.update({"protein", "filling"})
        notes.append("운동이나 단백질 니즈가 있어 단백질 있는 메뉴를 우선했어요.")

    if any(word in text for word in ["다이어트", "가볍", "붓", "붓기", "야식"]):
        wanted.update({"light", "protein"})
        avoid_tags.update({"high_sodium"})
        notes.append("가볍게 먹는 쪽이 좋아 보여 나트륨 높은 메뉴는 낮게 봤어요.")

    if any(word in text for word in ["설거지", "원팬", "원팟", "간단"]):
        wanted.update({"low_dishes", "one_pot", "one_pan"})
        notes.append("설거지를 줄일 수 있는 메뉴에 점수를 더 줬어요.")

    if any(word in text for word in ["맵게", "매운맛 좋아", "칼칼"]):
        wanted.add("spicy")
        notes.append("매콤한 메뉴 선호를 반영했어요.")

    if any(word in text for word in ["안 맵", "맵지", "약하게", "순하게"]):
        avoid_tags.add("spicy")
        notes.append("맵지 않은 쪽으로 추천했어요.")

    return wanted, avoid_tags, notes


def score_meal(
    meal: Meal,
    ingredients: set[str],
    avoid_items: set[str],
    available_tools: set[str],
    wanted_tags: set[str],
    avoid_tags: set[str],
    max_minutes: int,
    preferences: dict,
) -> tuple[int, list[str], list[str]]:
    blocked_items = avoid_items | set(preferences.get("allergies", [])) | set(preferences.get("dislikes", []))
    meal_items = meal.required | meal.optional
    if meal_items & blocked_items:
        return -999, [], [f"피해야 할 재료와 겹침: {', '.join(sorted(meal_items & blocked_items))}"]

    score = 0
    reasons: list[str] = []
    warnings: list[str] = []

    required_hits = meal.required & ingredients
    missing_required = meal.required - ingredients
    optional_hits = meal.optional & ingredients

    score += len(required_hits) * 8
    score += len(optional_hits) * 2
    score -= len(missing_required) * 5

    if required_hits:
        reasons.append(f"가지고 있는 핵심 재료 활용: {', '.join(sorted(required_hits))}")
    if optional_hits:
        reasons.append(f"추가 재료도 잘 맞음: {', '.join(sorted(optional_hits))}")
    if missing_required:
        warnings.append(f"부족한 핵심 재료: {', '.join(sorted(missing_required))}")

    matched_tags = meal.tags & wanted_tags
    risky_tags = meal.tags & avoid_tags
    score += len(matched_tags) * 4
    score -= len(risky_tags) * 7

    if matched_tags:
        reasons.append("상황과 맞는 점: " + ", ".join(TAG_LABELS[tag] for tag in sorted(matched_tags)))
    if risky_tags:
        warnings.append("오늘은 덜 맞을 수 있음: " + ", ".join(TAG_LABELS[tag] for tag in sorted(risky_tags)))

    if meal.minutes <= max_minutes:
        score += 4
        reasons.append(f"{meal.minutes}분 정도로 시간 안에 가능")
    else:
        score -= 6
        warnings.append(f"예상 조리시간 {meal.minutes}분으로 목표 시간보다 길 수 있음")

    if available_tools and meal.tools & available_tools:
        score += 3
        reasons.append(f"사용 가능한 도구와 맞음: {', '.join(sorted(meal.tools & available_tools))}")
    elif available_tools:
        score -= 4
        warnings.append(f"필요 도구 확인 필요: {', '.join(sorted(meal.tools))}")

    favorites = set(preferences.get("favorite_ingredients", []))
    favorite_hits = meal_items & favorites
    if favorite_hits:
        score += len(favorite_hits) * 2
        reasons.append(f"좋아하는 재료 포함: {', '.join(sorted(favorite_hits))}")

    return score, reasons, warnings


def recommend_meals(context: dict, preferences: dict) -> list[dict]:
    wanted_tags, avoid_tags, notes = analyze_needs(
        context["condition"],
        context["environment"],
        context["max_minutes"],
        context["spice_text"],
        preferences,
    )
    results = []
    for meal in MENU_CATALOG:
        score, reasons, warnings = score_meal(
            meal=meal,
            ingredients=context["ingredients"],
            avoid_items=context["avoid_items"],
            available_tools=context["tools"],
            wanted_tags=wanted_tags,
            avoid_tags=avoid_tags,
            max_minutes=context["max_minutes"],
            preferences=preferences,
        )
        if score > -100:
            results.append(
                {
                    "meal": meal,
                    "score": score,
                    "reasons": reasons,
                    "warnings": warnings,
                    "agent_notes": notes,
                }
            )
    return sorted(results, key=lambda item: item["score"], reverse=True)


def read_int(text: str, default: int) -> int:
    answer = ask(text, str(default))
    try:
        return int(answer)
    except ValueError:
        print(f"숫자로 읽지 못해서 기본값 {default}분으로 진행할게요.")
        return default


def collect_context(preferences: dict) -> dict:
    print("\n오늘의 상황을 알려주세요.")
    ingredients = parse_items(ask("가지고 있는 재료 예: 계란, 두부, 김치, 밥"))
    condition = ask("지금 컨디션 예: 피곤함, 속이 더부룩함, 운동 후")
    environment = ask("환경 예: 비 오는 저녁, 더운 점심, 설거지 적게")
    max_minutes = read_int("몇 분 안에 먹고 싶나요?", 20)
    avoid_items = parse_items(ask("오늘 피하고 싶은 재료/알레르기", ", ".join(preferences.get("allergies", []))))
    tools_default = ", ".join(preferences.get("tools", ["냄비", "프라이팬", "전자레인지"]))
    tools = parse_items(ask("사용 가능한 조리도구", tools_default))
    spice_text = ask("매운맛은 어느 정도가 좋아요?", preferences.get("spice_level", "보통"))

    return {
        "ingredients": ingredients,
        "condition": condition,
        "environment": environment,
        "max_minutes": max_minutes,
        "avoid_items": avoid_items,
        "tools": tools,
        "spice_text": spice_text,
    }


def print_recommendations(results: list[dict]) -> None:
    if not results:
        print("\n추천할 수 있는 메뉴를 찾지 못했어요. 피해야 할 재료를 조금 줄이거나 재료를 더 알려주세요.")
        return

    top_results = results[:3]
    notes = top_results[0]["agent_notes"]
    print("\n=== 에이전트 분석 ===")
    if notes:
        for note in dict.fromkeys(notes):
            print(f"- {note}")
    else:
        print("- 입력한 재료를 가장 잘 활용하는 쉬운 메뉴를 우선했어요.")

    print("\n=== 오늘의 추천 메뉴 TOP 3 ===")
    for index, result in enumerate(top_results, start=1):
        meal = result["meal"]
        print(f"\n{index}. {meal.name} ({meal.minutes}분, 난이도: {meal.difficulty})")
        for reason in result["reasons"][:4]:
            print(f"   - {reason}")
        if result["warnings"]:
            print(f"   - 확인: {result['warnings'][0]}")

    best = top_results[0]
    meal = best["meal"]
    print(f"\n=== 가장 추천하는 메뉴: {meal.name} ===")
    print(f"필요 재료: {', '.join(sorted(meal.required))}")
    if meal.optional:
        print(f"있으면 좋은 재료: {', '.join(sorted(meal.optional))}")
    print(f"조리도구: {', '.join(sorted(meal.tools))}")
    print("\n간단 레시피")
    for index, step in enumerate(meal.recipe, start=1):
        print(f"{index}. {step}")
    print(f"\n팁: {meal.tip}")

    avoid_messages = []
    for result in top_results:
        avoid_messages.extend(result["warnings"])
    if avoid_messages:
        print("\n오늘 조심할 점")
        for message in dict.fromkeys(avoid_messages[:3]):
            print(f"- {message}")


def print_preferences() -> None:
    preferences = load_preferences()
    print("\n=== 저장된 취향 ===")
    for key, label in [
        ("allergies", "알레르기"),
        ("dislikes", "피하고 싶은 재료"),
        ("favorite_ingredients", "좋아하는 재료"),
        ("diet_goal", "식단 목표"),
        ("spice_level", "매운맛 선호"),
        ("tools", "조리도구"),
    ]:
        value = preferences.get(key, "")
        if isinstance(value, list):
            value = ", ".join(value) if value else "없음"
        print(f"- {label}: {value or '없음'}")
    print()


def run_recommendation() -> None:
    preferences = load_preferences()
    context = collect_context(preferences)
    results = recommend_meals(context, preferences)
    print_recommendations(results)
    print("\n참고: 이 앱은 생활 식단 추천 도구예요. 질환, 알레르기, 임신 등 중요한 건강 이슈는 전문가 조언을 우선하세요.\n")


def main() -> None:
    print("오늘 뭐 먹지 Agent")
    print("재료, 컨디션, 환경을 보고 현실적인 한 끼를 추천해요.")

    while True:
        print("\n메뉴")
        print("1. 오늘 식단 추천 받기")
        print("2. 개인 취향 저장/수정")
        print("3. 저장된 취향 보기")
        print("4. 종료")

        choice = ask("선택", "1")
        if choice == "1":
            run_recommendation()
        elif choice == "2":
            edit_preferences()
        elif choice == "3":
            print_preferences()
        elif choice == "4":
            print("좋은 한 끼 챙겨 드세요!")
            break
        else:
            print("1~4 중에서 골라주세요.")


if __name__ == "__main__":
    main()
