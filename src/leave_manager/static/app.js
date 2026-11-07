// Status page (spec 0001, AC-3…AC-6). Data reaches the DOM via textContent only (docs/security.md).

const HEALTH_URL = "/api/v1/health";
const UNAVAILABLE_TEXT = "Sistem şu anda kullanılamıyor";

function renderLines(region, lines, state) {
  const paragraphs = lines.map((line) => {
    const paragraph = document.createElement("p");
    paragraph.textContent = line;
    return paragraph;
  });
  region.replaceChildren(...paragraphs);
  region.dataset.state = state;
}

async function loadStatus(region) {
  try {
    const response = await fetch(HEALTH_URL, { headers: { Accept: "application/json" } });
    if (!response.ok) {
      throw new Error(`status ${response.status}`);
    }
    const body = await response.json();
    if (body.status !== "ok" || body.database !== "reachable") {
      throw new Error("unexpected status");
    }
    renderLines(
      region,
      ["Sistem çalışıyor", `Sürüm: ${body.version}`, "Veritabanı: erişilebilir"],
      "success",
    );
  } catch {
    // No technical detail for the user (AC-5).
    renderLines(region, [UNAVAILABLE_TEXT], "error");
  }
}

loadStatus(document.getElementById("status"));
