const form = document.querySelector("#mealForm");
const resetButton = document.querySelector("#resetButton");
const emptyState = document.querySelector("#emptyState");
const results = document.querySelector("#results");
const analysisStrip = document.querySelector("#analysisStrip");
const mealList = document.querySelector("#mealList");
const recipePanel = document.querySelector("#recipePanel");
const timeBadge = document.querySelector("#timeBadge");

const samples = {
  rainy: {
    ingredients: "계란, 두부, 김치, 밥, 양파",
    condition: ["피곤함", "속이 더부룩함"],
    condition_other: "",
    environment: ["비 오는 날", "늦은 저녁", "설거지 적게"],
    environment_other: "",
    max_minutes: "20",
    avoid_items: "",
    tools: ["냄비", "프라이팬"],
    tools_other: "",
    spice_text: "약하게",
  },
  workout: {
    ingredients: "닭가슴살, 계란, 고구마, 채소, 토마토",
    condition: ["운동 후"],
    condition_other: "단백질을 챙기고 싶음",
    environment: ["더운 날"],
    environment_other: "",
    max_minutes: "15",
    avoid_items: "",
    tools: ["전자레인지", "그릇"],
    tools_other: "",
    spice_text: "보통",
  },
  late: {
    ingredients: "오트밀, 계란, 우유, 바나나",
    condition: ["가볍게 먹고 싶음"],
    condition_other: "속을 편하게 두고 싶음",
    environment: ["늦은 저녁", "설거지 적게"],
    environment_other: "10분 안에",
    max_minutes: "10",
    avoid_items: "라면",
    tools: ["전자레인지", "냄비"],
    tools_other: "",
    spice_text: "약하게",
  },
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function getSelectedValues(fieldName) {
  return Array.from(document.querySelectorAll(`.choice-grid[data-field="${fieldName}"] .option-pill.is-selected`))
    .map((button) => button.dataset.value)
    .filter(Boolean);
}

function setSelectedValues(fieldName, values) {
  document.querySelectorAll(`.choice-grid[data-field="${fieldName}"] .option-pill`).forEach((button) => {
    button.classList.toggle("is-selected", values.includes(button.dataset.value));
  });
}

function getChoiceText(fieldName, otherFieldName) {
  const data = new FormData(form);
  const selected = getSelectedValues(fieldName);
  const other = String(data.get(otherFieldName) || "").trim();
  return [...selected, other].filter(Boolean).join(", ");
}

function clearSelectedValues() {
  document.querySelectorAll(".option-pill.is-selected").forEach((button) => {
    button.classList.remove("is-selected");
  });
}

function getFormData() {
  const data = new FormData(form);
  return {
    ingredients: data.get("ingredients") || "",
    condition: getChoiceText("condition", "condition_other"),
    environment: getChoiceText("environment", "environment_other"),
    max_minutes: data.get("max_minutes") || "20",
    avoid_items: data.get("avoid_items") || "",
    tools: getChoiceText("tools", "tools_other"),
    spice_text: data.get("spice_text") || "보통",
  };
}

function fillSample(sampleName) {
  const sample = samples[sampleName];
  clearSelectedValues();
  Object.entries(sample).forEach(([key, value]) => {
    if (["condition", "environment", "tools"].includes(key)) {
      setSelectedValues(key, value);
      return;
    }
    const field = form.elements[key];
    if (field) field.value = value;
  });
}

function setLoading(isLoading) {
  const submitButton = form.querySelector(".primary-button");
  submitButton.disabled = isLoading;
  submitButton.querySelector("span").textContent = isLoading ? "추천 중" : "추천 받기";
  timeBadge.textContent = isLoading ? "분석 중" : "완료";
}

function renderNotes(notes) {
  analysisStrip.innerHTML = "";
  if (!notes.length) {
    analysisStrip.innerHTML = "<p>입력한 재료를 가장 잘 활용하는 메뉴를 우선했어요.</p>";
    return;
  }
  notes.forEach((note) => {
    const item = document.createElement("p");
    item.textContent = note;
    analysisStrip.appendChild(item);
  });
}

function renderMeals(meals) {
  mealList.innerHTML = "";
  meals.forEach((meal, index) => {
    const card = document.createElement("article");
    card.className = index === 0 ? "meal-card is-best" : "meal-card";
    card.innerHTML = `
      <div class="meal-rank">${index + 1}</div>
      <div class="meal-content">
        <div class="meal-title-row">
          <h3>${escapeHtml(meal.name)}</h3>
          <span>${escapeHtml(meal.minutes)}분</span>
        </div>
        <p class="meal-meta">난이도 ${escapeHtml(meal.difficulty)} · ${escapeHtml(meal.tools.join(", "))}</p>
        <ul>
          ${meal.reasons.slice(0, 3).map((reason) => `<li>${escapeHtml(reason)}</li>`).join("")}
        </ul>
        ${meal.warnings.length ? `<p class="warning-text">${escapeHtml(meal.warnings[0])}</p>` : ""}
      </div>
    `;
    mealList.appendChild(card);
  });
}

function renderRecipe(meal) {
  recipePanel.innerHTML = `
    <div class="recipe-heading">
      <div>
        <p class="eyebrow">Best Pick</p>
        <h3>${escapeHtml(meal.name)}</h3>
      </div>
      <span>${escapeHtml(meal.minutes)}분</span>
    </div>
    <div class="ingredient-row">
      <strong>필요 재료</strong>
      <p>${escapeHtml(meal.required.join(", "))}</p>
    </div>
    <div class="ingredient-row">
      <strong>있으면 좋은 재료</strong>
      <p>${escapeHtml(meal.optional.join(", ") || "없음")}</p>
    </div>
    <ol>
      ${meal.recipe.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}
    </ol>
    <p class="tip-text">${escapeHtml(meal.tip)}</p>
  `;
}

function renderPayload(payload) {
  if (!payload.meals.length) {
    emptyState.hidden = false;
    results.hidden = true;
    timeBadge.textContent = "결과 없음";
    return;
  }

  emptyState.hidden = true;
  results.hidden = false;
  renderNotes(payload.notes);
  renderMeals(payload.meals);
  renderRecipe(payload.meals[0]);
}

document.querySelectorAll(".sample-chip").forEach((button) => {
  button.addEventListener("click", () => fillSample(button.dataset.sample));
});

resetButton.addEventListener("click", () => {
  form.reset();
  clearSelectedValues();
  emptyState.hidden = false;
  results.hidden = true;
  timeBadge.textContent = "대기 중";
});

document.querySelectorAll(".option-pill").forEach((button) => {
  button.addEventListener("click", () => {
    button.classList.toggle("is-selected");
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setLoading(true);
  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getFormData()),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "요청에 실패했어요.");
    renderPayload(payload);
  } catch (error) {
    emptyState.hidden = false;
    results.hidden = true;
    emptyState.querySelector("h3").textContent = "문제가 생겼어요";
    emptyState.querySelector("p").textContent = error.message;
    timeBadge.textContent = "오류";
  } finally {
    setLoading(false);
  }
});
