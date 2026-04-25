from __future__ import annotations

from django.conf import settings


class AutoTranslateWidgetMiddleware:
    """Injects a Google Translate widget and language switcher into HTML pages."""

    EXCLUDED_PATH_PREFIXES = (
        "/admin/",
        "/api/",
        "/static/",
        "/media/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not self._should_inject(request, response):
            return response

        content = response.content.decode(response.charset or "utf-8")
        if "</body>" not in content:
            return response

        content = content.replace("</body>", f"{self._widget_snippet()}</body>")
        response.content = content.encode(response.charset or "utf-8")
        response["Content-Length"] = str(len(response.content))
        return response

    def _should_inject(self, request, response) -> bool:
        if any(request.path.startswith(prefix) for prefix in self.EXCLUDED_PATH_PREFIXES):
            return False

        content_type = response.get("Content-Type", "")
        return response.status_code == 200 and "text/html" in content_type

    def _widget_snippet(self) -> str:
        languages = getattr(
            settings,
            "SUPPORTED_SITE_LANGUAGES",
            [
                ("bg", "Bulgarian"),
                ("en", "English"),
                ("ru", "Russian"),
                ("tr", "Turkish"),
                ("de", "German"),
            ],
        )

        language_codes = [code for code, _ in languages]
        included_languages = ",".join(language_codes)
        options_json = repr([{"code": code, "label": label} for code, label in languages])

        return f"""
<style>
  .goog-te-banner-frame.skiptranslate,
  iframe.goog-te-banner-frame,
  .goog-te-balloon-frame,
  #goog-gt-tt,
  .goog-tooltip,
  .goog-tooltip:hover,
  .goog-te-spinner-pos,
  .skiptranslate iframe,
  .VIpgJd-ZVi9od-ORHb-OEVmcd,
  .VIpgJd-ZVi9od-l4eHX-hSRGPd,
  .VIpgJd-yAWNEb-L7lbkb,
  #goog-gt-vt,
  #goog-gt-tt,
  .goog-text-highlight {{
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
  }}

  body {{
    top: 0 !important;
  }}

  #auto-lang-widget {{
    position: fixed;
    top: 110px;
    right: 0;
    z-index: 9999;
    font-family: inherit;
  }}

  .lang-name {{
    text-transform: lowercase !important;
  }}

  #lang-drawer {{
    width: 58px;
    max-height: 54px;
    overflow: hidden;
    border-radius: 16px 0 0 16px;
    border: 1px solid rgba(255,255,255,0.4);
    backdrop-filter: blur(18px);
    background: linear-gradient(135deg, #1e88e5, #1565c0);
    color: #ffffff;
    box-shadow: 0 20px 50px rgba(0,0,0,0.25);
    transition: width .28s ease, max-height .32s ease, box-shadow .25s ease;
    backdrop-filter: blur(5px);
  }}

  #auto-lang-widget.open #lang-drawer {{
    width: 260px;
    max-height: 360px;
    box-shadow: 0 24px 52px rgba(2, 6, 23, 0.5);
  }}

  #lang-drawer-toggle {{
    width: 100%;
    min-height: 54px;
    border: 0;
    background: transparent;
    color: inherit;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 14px;
    text-align: left;
  }}

  #lang-drawer-toggle:hover {{
    background: rgba(148, 163, 184, 0.14);
  }}

  #lang-arrow {{
    font-size: 14px;
    opacity: .95;
    transform: translateX(0) rotate(0deg);
    transition: transform .3s ease;
  }}

  #auto-lang-widget.open #lang-arrow {{
    transform: translateX(2px) rotate(180deg);
  }}

  #lang-toggle-logo {{
    width: 22px;
    height: 22px;
    object-fit: contain;
    border-radius: 50%;
    background: #fff;
    padding: 2px;
  }}

  #lang-toggle-text {{
    font-size: 13px;
    font-weight: 700;
    letter-spacing: .01em;
    opacity: 0;
    transform: translateX(4px);
    transition: opacity .2s ease, transform .24s ease;
    white-space: nowrap;
  }}

  #auto-lang-widget.open #lang-toggle-text {{
    opacity: 1;
    transform: translateX(0);
  }}

  #lang-panel {{
    border-top: 1px solid rgba(148, 163, 184, 0.26);
    padding: 10px 10px 12px;
    opacity: 0;
    transform: translateY(-8px);
    transition: opacity .22s ease, transform .22s ease;
  }}

  #auto-lang-widget.open #lang-panel {{
    opacity: 1;
    transform: translateY(0);
  }}

  #lang-label {{
    display: block;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 8px;
    color: rgba(255,255,255,0.9);
  }}

  #lang-drawer::before{{
    content:"";
    position:absolute;
    inset:0;
    background: linear-gradient(
        to bottom,
        rgba(255,255,255,0.25),
        transparent 60%
    );
    pointer-events:none;
  }}

  #lang-list {{
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
    gap: 6px;
    max-height: 255px;
    overflow-y: auto;
  }}

  #lang-list li {{
    margin: 0;
    padding: 0;
  }}

  .lang-item-btn {{
    width: 100%;
    border: 1px solid transparent;
    border-radius: 10px;
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(10px);
    color: #f8fafc;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    cursor: pointer;
    font-size: 14px;
    line-height: 1.2;
    transition: background .2s ease, border-color .2s ease, transform .18s ease;
  }}

  .lang-item-btn:hover {{
    background: rgba(255,255,255,0.25);
    border-color: rgba(255,255,255,0.6);
    transform: translateX(-2px);
  }}

  .lang-item-btn.active {{
    background: rgba(46,125,50,0.25);
    border-color: rgba(46,125,50,0.8);
  }}

  .lang-flag {{
    font-size: 17px;
    width: 24px;
    text-align: center;
  }}

  .lang-name {{
    font-weight: 600;
  }}
</style>

<div id="auto-lang-widget" aria-label="Language switcher">
  <div id="lang-drawer">
    <button id="lang-drawer-toggle" type="button" aria-label="Translate" title="Translate">
      <span id="lang-arrow">❯</span>
      <img id="lang-toggle-logo" src="/media/buttons/Google_Translate_Icon.png" alt="Translate">
      <span id="lang-toggle-text">Превод</span>
    </button>

    <div id="lang-panel" aria-hidden="true">
      <label id="lang-label" for="lang-list">Language</label>
      <ul id="lang-list"></ul>
    </div>
  </div>
</div>

<div id="google_translate_element" style="display:none;"></div>

<script>
(function() {{
  const STORAGE_KEY = "varna_site_lang";
  const sourceLang = "bg";
  // CLEAR OLD COOKIE FIRST
  document.cookie = "googtrans=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;";
  document.cookie = "googtrans=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;domain=" + window.location.hostname + ";";

  function normalizeLanguage(code) {{
    const allowed = ["bg","en","ru","tr","de"];
    return allowed.includes(code) ? code : sourceLang;
  }}

  function setCookie(name, value) {{
    const hostname = window.location.hostname;
    const parts = hostname.split(".");
    const parentDomain = parts.length >= 2 ? `.${{parts.slice(-2).join(".")}}` : "";

    document.cookie = `${{name}}=${{value}};path=/;SameSite=Lax`;
    if (parentDomain) {{
      document.cookie = `${{name}}=${{value}};path=/;domain=${{parentDomain}};SameSite=Lax`;
    }}
  }}

  const stored = sourceLang;
  localStorage.setItem(STORAGE_KEY, sourceLang);

  setCookie("googtrans", `/${{sourceLang}}/${{stored}}`);
}})();
</script>

<script>
(function() {{
  const STORAGE_KEY = "varna_site_lang";
  const sourceLang = "bg";
  const languages = {options_json};
  let widgetUiInitialized = false;

  const flagMap = {{
    bg: "🇧🇬",
    en: "🇬🇧",
    ru: "🇷🇺",
    tr: "🇹🇷",
    de: "🇩🇪"
  }};

  let hasForcedNavigationReload = false;

  function setCookie(name, value, days, domain = "") {{
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    const domainPart = domain ? `;domain=${{domain}}` : "";
    document.cookie = `${{name}}=${{value}};expires=${{d.toUTCString()}};path=/;SameSite=Lax${{domainPart}}`;
  }}

  function getCookieDomainCandidates() {{
    const hostname = window.location.hostname;
    const looksLikeIpv4 = /^\\d+\\.\\d+\\.\\d+\\.\\d+$/.test(hostname);

    if (!hostname || hostname === "localhost" || looksLikeIpv4) {{
      return [""];
    }}

    const parts = hostname.split(".");
    const parentDomain = parts.length >= 2 ? `.${{parts.slice(-2).join(".")}}` : "";

    return Array.from(new Set(["", hostname, `.${{hostname}}`, parentDomain].filter(Boolean)));
  }}

  function setGoogTransCookie(value) {{
    const cookieDomains = getCookieDomainCandidates();
    cookieDomains.forEach((domain) => {{
      setCookie("googtrans", value, 365, domain);
    }});
  }}

  function normalizeLanguage(code) {{
    const requested = (code || "").toLowerCase();
    const hasLanguage = languages.some((lang) => lang.code === requested);
    return hasLanguage ? requested : sourceLang;
  }}

  function getStoredLanguage() {{
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? normalizeLanguage(saved) : sourceLang;
  }}

  function getCookieValue(name) {{
    const key = `${{name}}=`;
    const found = document.cookie
      .split(";")
      .map((part) => part.trim())
      .find((part) => part.startsWith(key));
    return found ? found.slice(key.length) : "";
  }}

  function setLanguage(targetLang) {{
    const normalized = normalizeLanguage(targetLang);
    localStorage.setItem(STORAGE_KEY, normalized);
    setGoogTransCookie(`/${{sourceLang}}/${{normalized}}`);
  }}

  function syncLanguageState() {{
    const selected = getStoredLanguage();
    const expectedCookieValue = `/${{sourceLang}}/${{selected}}`;
    const currentCookieValue = getCookieValue("googtrans");

    if (currentCookieValue !== expectedCookieValue) {{
      setLanguage(selected);
    }}

    return selected;
  }}

  function applySelectedLanguageToGoogleWidget(targetLang) {{
    const combo = document.querySelector(".goog-te-combo");
    if (!combo) return false;

    if (combo.value !== targetLang) {{
      combo.value = targetLang;
      combo.dispatchEvent(new Event("change"));
    }}
    return true;
  }}

  function hideGoogleTranslateBanner() {{
    document.body.style.top = "0px";
    const selectors = [
    "iframe.goog-te-banner-frame",
    ".goog-te-balloon-frame",
    "#goog-gt-tt",
    ".goog-tooltip",
    ".VIpgJd-ZVi9od-ORHb-OEVmcd",
    ".VIpgJd-ZVi9od-l4eHX-hSRGPd",
    ".VIpgJd-yAWNEb-L7lbkb"
  ];

    selectors.forEach((selector) => {{
      document.querySelectorAll(selector).forEach((node) => {{
        node.style.display = "none";
        node.style.visibility = "hidden";
        node.style.opacity = "0";
        node.style.pointerEvents = "none";
      }});
    }});
  }}

  function getDisplayName(code, uiLang) {{
    try {{
      if (typeof Intl !== "undefined" && Intl.DisplayNames) {{
        const dn = new Intl.DisplayNames([uiLang], {{ type: "language" }});
        return dn.of(code) || code;
      }}
    }} catch (e) {{}}

    const fallback = languages.find((lang) => lang.code === code);
    return fallback ? fallback.label : code;
  }}

  function getLanguageLabel(uiLang) {{
    const labelMap = {{
      bg: "Избери език",
      en: "Choose language",
      ru: "Выберите язык",
      tr: "Dil seç",
      de: "Sprache wählen"
    }};

    return labelMap[uiLang] || "Choose language";
  }}

  function getFlag(code) {{
    return flagMap[code] || "🌐";
  }}

  function renderLanguageOptions(currentLang) {{
    const list = document.getElementById("lang-list");
    const label = document.getElementById("lang-label");
    if (!list || !label) return;

    const uiLang = currentLang || sourceLang;
    const sorted = languages.slice().sort((a, b) =>
      getDisplayName(a.code, uiLang).localeCompare(getDisplayName(b.code, uiLang), uiLang)
    );

    label.textContent = getLanguageLabel(uiLang);
    list.innerHTML = "";

    sorted.forEach((lang) => {{
      const li = document.createElement("li");
      const btn = document.createElement("button");
      const flag = document.createElement("span");
      const name = document.createElement("span");

      btn.type = "button";
      btn.className = "lang-item-btn";
      if (lang.code === uiLang) {{
        btn.classList.add("active");
      }}
      btn.dataset.lang = lang.code;

      flag.className = "lang-flag";
      flag.textContent = getFlag(lang.code);

      name.className = "lang-name";
      name.textContent = getDisplayName(lang.code, uiLang).toLowerCase();

      btn.appendChild(flag);
      btn.appendChild(name);
      li.appendChild(btn);
      list.appendChild(li);

      btn.addEventListener("click", function() {{
        const langCode = btn.dataset.lang;
        setLanguage(langCode);
        renderLanguageOptions(langCode);
        applySelectedLanguageToGoogleWidget(langCode); // това вместо reload
      }});
    }});
  }}

    function initWidgetUI() {{
    if (widgetUiInitialized) return;

    const widget = document.getElementById("auto-lang-widget");
    const panel = document.getElementById("lang-panel");
    const toggleButton = document.getElementById("lang-drawer-toggle");
    if (!widget || !panel || !toggleButton) return;

    const selected = getStoredLanguage();
    renderLanguageOptions(selected);

    toggleButton.addEventListener("click", function() {{
      const isOpen = widget.classList.toggle("open");
      panel.setAttribute("aria-hidden", isOpen ? "false" : "true");
    }});

    document.addEventListener("click", function(event) {{
      if (!widget.contains(event.target)) {{
        widget.classList.remove("open");
        panel.setAttribute("aria-hidden", "true");
      }}
    }});

    widgetUiInitialized = true;
  }}

  function reapplyGoogleTranslation(targetLang, attemptsLeft = 30) {{
    if (applySelectedLanguageToGoogleWidget(targetLang)) {{
      return;
    }}

    if (attemptsLeft <= 0) {{
      return;
    }}

    setTimeout(function() {{
      reapplyGoogleTranslation(targetLang, attemptsLeft - 1);
    }}, 150);
  }}

  function ensureLanguageApplied(targetLang, allowReloadFallback = false) {{
    const normalized = normalizeLanguage(targetLang);

    syncLanguageState();
    renderLanguageOptions(normalized);
    reapplyGoogleTranslation(normalized);

    if (!allowReloadFallback || normalized === sourceLang || hasForcedNavigationReload) {{
      return;
    }}

    setTimeout(function() {{
      const stillNotApplied = !applySelectedLanguageToGoogleWidget(normalized);
      if (stillNotApplied) {{
          hasForcedNavigationReload = true;
          window.location.reload();
      }}
    }}, 2600);
  }}

  function forceLanguageImmediately() {{
      const target = localStorage.getItem("varna_site_lang") || "bg";

      function tryApply() {{
        const combo = document.querySelector(".goog-te-combo");

        if (combo) {{
          combo.value = target;
          combo.dispatchEvent(new Event("change"));
          return true;
        }}
        return false;
      }}

      let attempts = 0;

      const interval = setInterval(function() {{
        if (tryApply() || attempts > 20) {{
          clearInterval(interval);
        }}
        attempts++;
      }}, 100);
    }}

  window.addEventListener("DOMContentLoaded", function() {{
      const target = document.documentElement;

      if (target) {{
        const bannerObserver = new MutationObserver(hideGoogleTranslateBanner);
        bannerObserver.observe(target, {{ childList: true, subtree: true }});
      }}
    }});
  setInterval(hideGoogleTranslateBanner, 400);
  syncLanguageState();
  initWidgetUI();

  window.googleTranslateElementInit = function() {{
    new google.translate.TranslateElement({{
      pageLanguage: sourceLang,
      includedLanguages: "{included_languages}",
      autoDisplay: false
    }}, "google_translate_element");

    hideGoogleTranslateBanner();
    initWidgetUI();
    const selected = syncLanguageState();
    forceLanguageImmediately();
    ensureLanguageApplied(selected, false);
  }};

function reapplyTranslationAfterHistoryNavigation() {{
    const selected = syncLanguageState();
    initWidgetUI();
    ensureLanguageApplied(selected, true);
  }}

  window.addEventListener("pageshow", function() {{
    setTimeout(reapplyTranslationAfterHistoryNavigation, 0);
  }});

  window.addEventListener("popstate", function() {{
    setTimeout(reapplyTranslationAfterHistoryNavigation, 0);
  }});
}})();
</script>

<script src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
"""