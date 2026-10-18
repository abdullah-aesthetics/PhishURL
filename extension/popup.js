const COLORS = { Low: "#3dffa0", Medium: "#ffb020", High: "#ff4d5e" };
(async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  document.getElementById("url").textContent = tab.url;
  const v = document.getElementById("verdict");
  try {
    const res = await fetch("http://localhost:8000/scan", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ url: tab.url }) });
    const r = await res.json();
    v.textContent = `${r.verdict} · ${r.level} risk (${Math.round(r.risk * 100)}%)`;
    v.style.color = COLORS[r.level];
    const fill = document.getElementById("fill");
    fill.style.background = COLORS[r.level];
    requestAnimationFrame(() => (fill.style.width = Math.round(r.risk * 100) + "%"));
    const ul = document.getElementById("reasons");
    (r.reasons.length ? r.reasons : [{ severity: "low", text: "No suspicious URL patterns found." }]).forEach((x) => {
      const li = document.createElement("li");
      li.className = x.severity;
      li.textContent = x.text;
      ul.appendChild(li);
    });
  } catch (e) {
    v.textContent = "API not reachable";
    v.style.color = "#9ca3af";
  }
})();
