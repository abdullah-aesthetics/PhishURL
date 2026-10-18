const API = "http://localhost:8000/scan";
const COLORS = { Low: "#22c55e", Medium: "#f59e0b", High: "#ef4444" };
const TEXT = { Low: "OK", Medium: "!", High: "!!" };

async function check(tabId, url) {
  if (!/^https?:/.test(url)) return;
  try {
    const res = await fetch(API, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ url }) });
    const r = await res.json();
    chrome.action.setBadgeText({ tabId, text: TEXT[r.level] });
    chrome.action.setBadgeBackgroundColor({ tabId, color: COLORS[r.level] });
  } catch (e) {
    chrome.action.setBadgeText({ tabId, text: "?" });
    chrome.action.setBadgeBackgroundColor({ tabId, color: "#6b7280" });
  }
}
chrome.tabs.onUpdated.addListener((id, info, tab) => {
  if (info.status === "complete" && tab.url) check(id, tab.url);
});
