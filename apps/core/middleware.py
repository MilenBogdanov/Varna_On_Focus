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
    right: 20px;
    z-index: 9999;
  }}

  #lang-toggle-btn {{
    width: 52px;
    height: 52px;
    border: 0;
    border-radius: 50%;
    box-shadow: 0 8px 24px rgba(0, 0, 0, .22);
    background: #ffffff;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
  }}

  #lang-toggle-btn:hover {{
    transform: scale(1.04);
  }}

  #lang-toggle-btn img {{
    width: 28px;
    height: 28px;
  }}

  #lang-panel {{
    margin-top: 10px;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, .18);
    padding: 10px;
    min-width: 210px;
    display: none;
  }}

  #auto-lang-widget.open #lang-panel {{
    display: block;
  }}

  #lang-label {{
    display: block;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 6px;
    color: #1f2937;
  }}

  #lang-select {{
    width: 100%;
    padding: 7px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 14px;
    color: #111827;
    background: #fff;
  }}
</style>

<div id="auto-lang-widget" aria-label="Language switcher">
  <button id="lang-toggle-btn" type="button" aria-label="Translate" title="Translate">
    <img src="/media/buttons/Google_Translate_Icon.png" alt="Translate">
  </button>

  <div id="lang-panel">
    <label id="lang-label" for="lang-select">Language</label>
    <select id="lang-select"></select>
  </div>
</div>

<div id="google_translate_element" style="display:none;"></div>

<script>
(function() {{
  const STORAGE_KEY = "varna_site_lang";
  const sourceLang = "bg";
  const languages = {options_json};

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
      bg: "Език",
      en: "Language",
      ru: "Язык",
      tr: "Dil",
      de: "Sprache"
    }};

    return labelMap[uiLang] || "Language";
  }}

  function renderLanguageOptions(currentLang) {{
    const select = document.getElementById("lang-select");
    const label = document.getElementById("lang-label");
    if (!select) return;

    const uiLang = currentLang || sourceLang;
    const sorted = languages.slice().sort((a, b) =>
      getDisplayName(a.code, uiLang).localeCompare(getDisplayName(b.code, uiLang), uiLang)
    );

    select.innerHTML = sorted
      .map((lang) => `<option value="${{lang.code}}">${{getDisplayName(lang.code, uiLang)}}</option>`)
      .join("");

    select.value = uiLang;
    label.textContent = getLanguageLabel(uiLang);
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
    const toggleButton = document.getElementById("lang-toggle-btn");
    const langSelect = document.getElementById("lang-select");

    const selected = getStoredLanguage();
    renderLanguageOptions(selected);

    toggleButton.addEventListener("click", function() {{
      widget.classList.toggle("open");
    }});

    langSelect.addEventListener("change", function() {{
      setLanguage(langSelect.value);
      renderLanguageOptions(langSelect.value);
      window.location.reload();
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