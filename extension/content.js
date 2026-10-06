(function () {
  "use strict";

  const API_URL = "http://127.0.0.1:8765/analyze";
  const seen = new WeakSet();
  let activeArticle = null;
  let requestId = 0;

  function textFromArticle(article) {
    const clone = article.cloneNode(true);
    clone.querySelectorAll(".trustcheck-panel").forEach((panel) => panel.remove());
    const visibleText = (clone.innerText || clone.textContent || "").replace(/\s+/g, " ").trim();
    const imageDescriptions = [...article.querySelectorAll("img[alt]")]
      .map((image) => image.alt.trim())
      .filter((alt) => alt && !/^photo by /i.test(alt));
    return [visibleText, ...imageDescriptions].join(" ").slice(0, 12000);
  }

  function addPanel(article) {
    if (seen.has(article)) return;
    seen.add(article);
    if (getComputedStyle(article).position === "static") article.style.position = "relative";
    const panel = document.createElement("div");
    panel.className = "trustcheck-panel";
    panel.innerHTML = "<div>TrustCheck : prêt</div><button type=\"button\">Analyser ce post</button><div class=\"trustcheck-result\"></div>";
    const button = panel.querySelector("button");
    const result = panel.querySelector(".trustcheck-result");
    button.addEventListener("click", async () => {
      activeArticle = article;
      const currentRequest = ++requestId;
      button.disabled = true;
      result.textContent = "Analyse en cours…";
      try {
        const response = await fetch(API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: textFromArticle(article) })
        });
        const payload = await response.json();
        if (currentRequest !== requestId || activeArticle !== article) return;
        if (!response.ok) throw new Error(payload.error || "API indisponible");
        result.replaceChildren(...formatResults(payload));
      } catch (error) {
        if (currentRequest === requestId) result.textContent = `Impossible d’analyser : ${error.message}`;
      } finally {
        button.disabled = false;
      }
    });
    article.appendChild(panel);
  }

  function formatResults(analysis) {
    const fragment = document.createDocumentFragment();
    if (!(analysis.results || []).length) {
      const empty = document.createElement("div");
      empty.textContent = "Aucune affirmation factuelle détectée dans le texte accessible.";
      fragment.appendChild(empty);
      return [fragment];
    }
    for (const item of (analysis.results || [])) {
      const block = document.createElement("div");
      const confidenceKind = item.confidence_kind || "confiance factuelle";
      block.textContent = `Affirmation : ${item.claim.text}\n${item.verdict} — ${confidenceKind} : ${Math.round(item.confidence * 100)} % — ${item.explanation}`;
      for (const source of (item.sources || []).slice(0, 3)) {
        const link = document.createElement("a");
        link.className = "trustcheck-source";
        link.href = source.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = source.title;
        block.appendChild(link);
      }
      fragment.appendChild(block);
    }
    return [fragment];
  }

  const observer = new MutationObserver(() => document.querySelectorAll("article").forEach(addPanel));
  observer.observe(document.documentElement, { childList: true, subtree: true });
  document.querySelectorAll("article").forEach(addPanel);
})();
