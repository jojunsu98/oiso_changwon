"use strict";

const LEVELS = ["해당 가능", "조건부 해당 가능", "직접 확인", "해당 없음"];

const state = {
  profile: null,
  policies: [],
};

const qs = (selector, scope = document) => scope.querySelector(selector);
const qsa = (selector, scope = document) => [...scope.querySelectorAll(selector)];

function setLoading(form, loading) {
  const button = qs('button[type="submit"]', form);
  if (!button) return;
  button.disabled = loading;
  button.classList.toggle("is-loading", loading);
  form.setAttribute("aria-busy", String(loading));
}

function setMessage(element, message = "", kind = "error") {
  element.textContent = message;
  element.classList.toggle("success", kind === "success");
}

async function fetchJson(url, options = {}, timeoutMs = 30000) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });

    let data = {};
    try {
      data = await response.json();
    } catch {
      data = {};
    }

    if (!response.ok) {
      throw new Error(data.message || `요청을 처리하지 못했습니다. (${response.status})`);
    }
    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("응답이 지연되고 있습니다. 잠시 후 다시 시도해 주세요.");
    }
    if (error instanceof TypeError) {
      throw new Error("서버에 연결하지 못했습니다. 인터넷 연결 또는 배포 상태를 확인해 주세요.");
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

function setupNavigation() {
  const toggle = qs(".menu-toggle");
  const nav = qs("#primary-nav");
  if (!toggle || !nav) return;

  const closeMenu = () => {
    nav.classList.remove("open");
    toggle.setAttribute("aria-expanded", "false");
    document.body.classList.remove("menu-open");
  };

  toggle.addEventListener("click", () => {
    const nextOpen = !nav.classList.contains("open");
    nav.classList.toggle("open", nextOpen);
    toggle.setAttribute("aria-expanded", String(nextOpen));
    document.body.classList.toggle("menu-open", nextOpen);
  });

  qsa("a", nav).forEach((link) => link.addEventListener("click", closeMenu));
  window.addEventListener("resize", () => {
    if (window.innerWidth > 860) closeMenu();
  });
}

function getProfilePayload(form) {
  const data = new FormData(form);
  return {
    age: Number(data.get("age")),
    move_in_date: String(data.get("move_in_date") || ""),
    job_type: String(data.get("job_type") || ""),
    employed_in_changwon: data.get("employed_in_changwon") === "true",
    previous_residence_years: Number(data.get("previous_residence_years")),
    vehicle: String(data.get("vehicle") || ""),
  };
}

function validateProfile(profile) {
  if (!Number.isInteger(profile.age) || profile.age < 18 || profile.age > 100) {
    return "만 나이를 18세부터 100세 사이로 입력해 주세요.";
  }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(profile.move_in_date)) {
    return "창원 전입일을 입력해 주세요.";
  }
  if (!profile.job_type) return "현재 하는 일을 선택해 주세요.";
  if (!profile.vehicle) return "차량 보유 여부를 선택해 주세요.";
  if (!Number.isFinite(profile.previous_residence_years)) {
    return "전입 전 타지역 거주 기간을 선택해 주세요.";
  }
  return "";
}

function makeElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined && text !== null) element.textContent = text;
  return element;
}

function renderLevelCounts(counts = {}) {
  const container = qs("#level-counts");
  container.replaceChildren();

  LEVELS.forEach((level) => {
    const item = makeElement("div", "level-count");
    item.dataset.level = level;
    item.append(
      makeElement("span", "", level),
      makeElement("strong", "", String(counts[level] ?? 0)),
    );
    container.append(item);
  });
}

function appendList(container, className, items) {
  if (!Array.isArray(items) || items.length === 0) return;
  const list = makeElement("ul", className);
  items.forEach((item) => list.append(makeElement("li", "", item)));
  container.append(list);
}

function renderPolicyCard(policy) {
  const article = makeElement("article", "policy-card");
  article.dataset.level = policy.level;

  const head = makeElement("div", "policy-card-head");
  head.append(
    makeElement("h4", "", policy.name || "정책명 확인 필요"),
    makeElement("span", "status-pill", policy.level || "직접 확인"),
  );
  head.lastElementChild.dataset.level = policy.level;
  article.append(head);

  const meta = makeElement("div", "policy-meta");
  [policy.category, policy.status, policy.checked ? `확인 ${policy.checked}` : ""].filter(Boolean).forEach((value) => {
    meta.append(makeElement("span", "", value));
  });
  if (meta.childElementCount) article.append(meta);

  if (policy.message) article.append(makeElement("p", "", policy.message));
  if (policy.support) {
    const support = makeElement("p", "");
    support.append(makeElement("strong", "", "지원 내용: "), document.createTextNode(policy.support));
    article.append(support);
  }

  appendList(article, "reason-list", policy.reasons);
  appendList(article, "schedule-list", policy.schedule);

  if (policy.how_to_apply && policy.level !== "해당 없음") {
    const method = makeElement("p", "");
    method.append(makeElement("strong", "", "확인·신청: "), document.createTextNode(policy.how_to_apply));
    article.append(method);
  }

  if (policy.link) {
    const link = makeElement("a", "policy-link", "공식 확인 경로 열기 →");
    link.href = policy.link;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    article.append(link);
  }

  return article;
}

function renderPolicyList(filter = "all") {
  const container = qs("#policy-list");
  const countText = qs("#policy-result-count");
  const filtered = filter === "all"
    ? state.policies
    : state.policies.filter((policy) => policy.level === filter);

  container.replaceChildren();
  countText.textContent = `${filtered.length}개 결과 표시`;

  if (!filtered.length) {
    container.append(makeElement("div", "empty-state", "선택한 단계에 해당하는 결과가 없습니다."));
    return;
  }

  filtered.forEach((policy) => container.append(renderPolicyCard(policy)));
}

function renderRecommendation(data) {
  state.policies = Array.isArray(data.results) ? data.results : [];

  renderLevelCounts(data.counts || {});
  qs("#level-filter").value = "all";
  renderPolicyList("all");

  const summaryBox = qs("#ai-summary");
  const summaryText = qs("#ai-summary-text");
  const ai = data.ai || {};
  summaryBox.classList.toggle("warning", !ai.available);
  summaryText.textContent = ai.summary || ai.message || "구조화된 정책 판정 결과를 확인해 주세요.";

  const results = qs("#results");
  results.hidden = false;
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function setupProfileForm() {
  const form = qs("#profile-form");
  const message = qs("#profile-message");
  const filter = qs("#level-filter");
  const reset = qs("#reset-results");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    setMessage(message, "");

    if (!form.checkValidity()) {
      form.reportValidity();
      setMessage(message, "필수 항목을 모두 입력해 주세요.");
      return;
    }

    const profile = getProfilePayload(form);
    const validationError = validateProfile(profile);
    if (validationError) {
      setMessage(message, validationError);
      return;
    }

    setLoading(form, true);
    try {
      const data = await fetchJson("/api/recommend", {
        method: "POST",
        body: JSON.stringify(profile),
      }, 35000);
      state.profile = profile;
      renderRecommendation(data);
      setMessage(message, "맞춤 결과를 만들었습니다.", "success");
    } catch (error) {
      setMessage(message, error.message);
    } finally {
      setLoading(form, false);
    }
  });

  filter.addEventListener("change", () => renderPolicyList(filter.value));

  reset.addEventListener("click", () => {
    qs("#results").hidden = true;
    form.scrollIntoView({ behavior: "smooth", block: "center" });
    qs("#age").focus({ preventScroll: true });
  });
}

function addChatBubble(text, type = "assistant", extraClass = "") {
  const output = qs("#chat-output");
  const bubble = makeElement("div", `chat-bubble ${type}-bubble ${extraClass}`.trim(), text);
  output.append(bubble);
  output.scrollTop = output.scrollHeight;
  return bubble;
}

function renderChatSources(sources) {
  if (!Array.isArray(sources) || !sources.length) return;
  const output = qs("#chat-output");
  const box = makeElement("div", "chat-sources");
  box.append(makeElement("strong", "", "답변에 참고한 자료"));

  sources.slice(0, 5).forEach((source) => {
    if (source.url) {
      const link = makeElement("a", "", `· ${source.title}`);
      link.href = source.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      box.append(link);
    } else {
      box.append(makeElement("span", "", `· ${source.title}`));
    }
  });

  output.append(box);
  output.scrollTop = output.scrollHeight;
}

function moveQuestionToChat(question) {
  const input = qs("#chat-input");
  input.value = question;
  input.dispatchEvent(new Event("input"));
  qs("#assistant").scrollIntoView({ behavior: "smooth", block: "start" });
  window.setTimeout(() => input.focus(), 450);
}

function setupChat() {
  const form = qs("#chat-form");
  const input = qs("#chat-input");
  const counter = qs("#char-count");
  const message = qs("#chat-message");

  input.addEventListener("input", () => {
    counter.textContent = `${input.value.length}/500`;
  });

  qsa("[data-question]").forEach((button) => {
    button.addEventListener("click", () => moveQuestionToChat(button.dataset.question));
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    setMessage(message, "");
    const question = input.value.trim();

    if (!question) {
      setMessage(message, "질문을 입력해 주세요.");
      input.focus();
      return;
    }

    addChatBubble(question, "user");
    input.value = "";
    input.dispatchEvent(new Event("input"));
    setLoading(form, true);
    const loadingBubble = addChatBubble("확인된 자료에서 관련 내용을 찾는 중입니다…", "assistant");

    try {
      const data = await fetchJson("/api/chat", {
        method: "POST",
        body: JSON.stringify({
          message: question,
          profile: state.profile,
        }),
      }, 40000);
      loadingBubble.remove();
      addChatBubble(data.answer || "답변을 만들지 못했습니다. 다시 시도해 주세요.", "assistant");
      renderChatSources(data.sources);
    } catch (error) {
      loadingBubble.remove();
      addChatBubble(error.message, "assistant", "error-bubble");
    } finally {
      setLoading(form, false);
    }
  });
}

function setupDateField() {
  const dateField = qs("#move-in-date");
  if (!dateField) return;
  const today = new Date();
  const localDate = new Date(today.getTime() - today.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 10);
  dateField.setAttribute("data-today", localDate);
}

function init() {
  setupNavigation();
  setupProfileForm();
  setupChat();
  setupDateField();
}

document.addEventListener("DOMContentLoaded", init);
