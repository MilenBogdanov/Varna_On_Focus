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
    border: 1px solid rgba(255, 255, 255, 0.35);
    background: linear-gradient(165deg, #0f172a 0%, #1e293b 48%, #334155 100%);
    color: #ffffff;
    box-shadow: 0 18px 42px rgba(2, 6, 23, 0.42);
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
    color: #e2e8f0;
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
    background: rgba(15, 23, 42, 0.65);
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
    background: rgba(51, 65, 85, 0.9);
    border-color: rgba(148, 163, 184, 0.5);
    transform: translateX(-2px);
  }}

  .lang-item-btn.active {{
    background: rgba(34, 197, 94, 0.22);
    border-color: rgba(74, 222, 128, 0.9);
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
  const languages = {options_json};

  const flagMap = {{
    bg: "🇧🇬",
    en: "🇬🇧",
    ru: "🇷🇺",
    tr: "🇹🇷",
    de: "🇩🇪"
  }};

  function setCookie(name, value, days) {{
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = `${{name}}=${{value}};expires=${{d.toUTCString()}};path=/`;
  }}

  function getStoredLanguage() {{
    return localStorage.getItem(STORAGE_KEY) || sourceLang;
  }}

  function setLanguage(targetLang) {{
    localStorage.setItem(STORAGE_KEY, targetLang);
    setCookie("googtrans", `/${{sourceLang}}/${{targetLang}}`, 365);
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
        window.location.reload();
      }});
    }});
  }}

  const bannerObserver = new MutationObserver(hideGoogleTranslateBanner);
  bannerObserver.observe(document.documentElement, {{ childList: true, subtree: true }});
  setInterval(hideGoogleTranslateBanner, 400);

  window.googleTranslateElementInit = function() {{
    new google.translate.TranslateElement({{
      pageLanguage: sourceLang,
      includedLanguages: "{included_languages}",
      autoDisplay: false
    }}, "google_translate_element");

    hideGoogleTranslateBanner();

    const widget = document.getElementById("auto-lang-widget");
    const panel = document.getElementById("lang-panel");
    const toggleButton = document.getElementById("lang-drawer-toggle");

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

    const currentCookie = document.cookie.includes("googtrans=");
    if (!currentCookie) {{
      setLanguage(selected);
      if (selected !== sourceLang) {{
        window.location.reload();
      }}
    }}
  }};
}})();
</script>

<script src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
"""