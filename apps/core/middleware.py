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

        content = content.replace("</body>", f"{self._widget_snippet(request)}</body>")
        response.content = content.encode(response.charset or "utf-8")
        response["Content-Length"] = str(len(response.content))
        return response

    def _should_inject(self, request, response) -> bool:
        if any(request.path.startswith(prefix) for prefix in self.EXCLUDED_PATH_PREFIXES):
            return False

        content_type = response.get("Content-Type", "")
        return response.status_code == 200 and "text/html" in content_type

    def _widget_snippet(self, request) -> str:
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

        import json
        language_codes = [code for code, _ in languages]
        included_languages = ",".join(language_codes)
        options_json = json.dumps(
            [{"code": code, "label": label} for code, label in languages],
            ensure_ascii=False,
        )

        return f"""
<style>
  .goog-te-banner-frame.skiptranslate,
  iframe.goog-te-banner-frame,
  .goog-te-balloon-frame,
  #goog-gt-tt,
  .goog-tooltip,
  .goog-tooltip:hover,
  .goog-te-spinner-pos,
  .goog-te-spinner,
  .goog-spinner-pos,
  .skiptranslate iframe,
  .VIpgJd-ZVi9od-ORHb-OEVmcd,
  .VIpgJd-ZVi9od-l4eHX-hSRGPd,
  .VIpgJd-yAWNEb-L7lbkb,
  .VIpgJd-ZVi9od-aZ2wEe,
  .VIpgJd-ZVi9od-aZ2wEe-OiiCO,
  #goog-gt-vt,
  #goog-gt-tt,
  .goog-text-highlight,
  #goog-wt-spinner {{
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
  }}

  body {{
    top: 0 !important;
  }}

  body.gt-loading {{
    opacity: 0 !important;
    pointer-events: none !important;
  }}

  body.gt-ready {{
    opacity: 1;
    transition: opacity 0.3s ease;
  }}

  #gt-loading-overlay {{
    position: fixed;
    inset: 0;
    z-index: 99999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 20px;
    background: linear-gradient(160deg, #0d2b6b 0%, #1565c0 60%, #1e88e5 100%);
    opacity: 1;
    transition: opacity 0.35s ease;
  }}

  #gt-loading-overlay.gt-overlay-hide {{
    opacity: 0;
    pointer-events: none;
  }}

  .gt-spinner-ring {{
    width: 72px;
    height: 72px;
    border-radius: 50%;
    border: 5px solid rgba(255,255,255,0.15);
    border-top-color: #ffffff;
    border-right-color: rgba(255,255,255,0.6);
    animation: gt-spin 0.9s cubic-bezier(0.55,0.15,0.45,0.85) infinite;
    box-shadow: 0 0 28px rgba(255,255,255,0.15);
  }}

  @keyframes gt-spin {{
    to {{ transform: rotate(360deg); }}
  }}

  .gt-loading-logo {{
    width: 54px;
    height: 54px;
    position: absolute;
    border-radius: 50%;
    object-fit: contain;
    padding: 6px;
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(4px);
  }}

  .gt-spinner-wrap {{
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 72px;
    height: 72px;
  }}

  .gt-loading-text {{
    font-family: inherit, system-ui, sans-serif;
    font-size: 15px;
    font-weight: 600;
    color: rgba(255,255,255,0.9);
    letter-spacing: 0.04em;
    text-shadow: 0 1px 8px rgba(0,0,0,0.25);
  }}

  .gt-loading-dots span {{
    animation: gt-blink 1.2s infinite;
    opacity: 0;
  }}
  .gt-loading-dots span:nth-child(1) {{ animation-delay: 0s; }}
  .gt-loading-dots span:nth-child(2) {{ animation-delay: 0.2s; }}
  .gt-loading-dots span:nth-child(3) {{ animation-delay: 0.4s; }}

  @keyframes gt-blink {{
    0%, 80%, 100% {{ opacity: 0; }}
    40% {{ opacity: 1; }}
  }}

  #auto-lang-widget {{
    position: fixed;
    top: 110px;
    right: 0;
    z-index: 9999;
    font-family: inherit;
  }}

  #lang-drawer{{
    width: 58px;
    max-height: 54px;
    overflow: hidden;

    border-radius: 16px 0 0 16px;

    /* 🔥 GLASS STYLE */
    background: rgba(255,255,255,0.08);

    backdrop-filter: blur(26px) saturate(180%);
    -webkit-backdrop-filter: blur(26px) saturate(180%);

    border: 1px solid rgba(255,255,255,0.35);

    box-shadow:
        0 25px 60px rgba(0,0,0,0.25),
        inset 0 1px 0 rgba(255,255,255,0.5);

    color: #ffffff;

    transition: width .28s ease,
                max-height .32s ease,
                box-shadow .25s ease,
                transform .25s ease;
    }}
    
    #lang-drawer::before{{
    content:"";
    position:absolute;
    inset:0;

    background: linear-gradient(
        to bottom,
        rgba(255,255,255,0.25),
        rgba(255,255,255,0.05) 40%,
        transparent 70%
    );

    pointer-events:none;
}}

#lang-drawer:hover{{
    transform: translateY(-3px) scale(1.02);

    box-shadow:
        0 35px 80px rgba(0,0,0,0.35),
        inset 0 1px 0 rgba(255,255,255,0.7);
}}

  #auto-lang-widget.open #lang-drawer{{
    width: 260px;
    max-height: 360px;

    box-shadow:
        0 40px 90px rgba(0,0,0,0.45),
        inset 0 1px 0 rgba(255,255,255,0.7);
}}

#lang-drawer,
#lang-drawer *{{
    text-shadow:
        0 1px 2px rgba(0,0,0,0.4),
        0 2px 6px rgba(0,0,0,0.2);
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
    background: rgba(148,163,184,0.14);
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
    border-top: 1px solid rgba(148,163,184,0.26);
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

  #lang-drawer::before {{
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom, rgba(255,255,255,0.25), transparent 60%);
    pointer-events: none;
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
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 10px;
  background: rgba(0,0,0,0.18);               /* ← беше rgba(255,255,255,0.10) */
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
    background: rgba(0,0,0,0.28);               /* ← беше rgba(255,255,255,0.22) */
  border-color: rgba(255,255,255,0.45);
  transform: translateX(-2px);
  }}

  .lang-item-btn.active {{
    background: rgba(46,125,50,0.35);           /* ← леко по-наситено зелено */
  border-color: rgba(46,125,50,0.8);
  }}

  .lang-flag {{
    font-size: 17px;
    width: 24px;
    text-align: center;
  }}

  .lang-name {{
    font-weight: 600;
    text-transform: lowercase;
  }}
</style>

<div id="auto-lang-widget" aria-label="Language switcher">
  <div id="lang-drawer">
    <button id="lang-drawer-toggle" type="button" aria-label="Translate" title="Translate">
      <span id="lang-arrow">❯</span>
      <img id="lang-toggle-logo" src="/media/buttons/Google_Translate_Icon.png" alt="Translate">
      <span id="lang-toggle-text">Превод / Translation</span>
    </button>
    <div id="lang-panel" aria-hidden="true">
      <label id="lang-label" for="lang-list">Language</label>
      <ul id="lang-list"></ul>
    </div>
  </div>
</div>

<div id="google_translate_element" style="display:none;"></div>

<div id="gt-loading-overlay" style="display:none;">
  <div class="gt-spinner-wrap">
    <div class="gt-spinner-ring"></div>
    <img class="gt-loading-logo" src="/media/buttons/Google_Translate_Icon.png" alt="">
  </div>
  <div class="gt-loading-text">
    Превод<span class="gt-loading-dots"><span>.</span><span>.</span><span>.</span></span>
  </div>
</div>

<script>
(function() {{

  // ── КОНСТАНТИ ───────────────────────────────────────────────
  const STORAGE_KEY = "varna_site_lang_session";
  const INIT_KEY    = "varna_site_lang_initialized";
  const sourceLang  = "bg";
  const languages   = {options_json};
  const flagMap     = {{ bg:"🇧🇬", en:"🇬🇧", ru:"🇷🇺", tr:"🇹🇷", de:"🇩🇪" }};
  let widgetUiInitialized = false;

  // Ключът включва pathname → автоматично се нулира при нова страница
  function reloadKey() {{
    return "gt_reloaded_v2_" + window.location.pathname;
  }}

  // ── НОРМАЛИЗИРАНЕ ───────────────────────────────────────────
  function normalizeLanguage(code) {{
    const c = (code || "").toLowerCase();
    return languages.some(function(l) {{ return l.code === c; }}) ? c : sourceLang;
  }}

  // ── COOKIE ФУНКЦИИ ──────────────────────────────────────────
  function getCookieDomains() {{
    const h = window.location.hostname;
    if (!h || h === "localhost" || /^\d+\.\d+\.\d+\.\d+$/.test(h)) return [""];
    const parts = h.split(".");
    const parent = parts.length >= 2 ? "." + parts.slice(-2).join(".") : "";
    return Array.from(new Set(["", h, "." + h, parent].filter(Boolean)));
  }}

  function setCookie(name, value, days, domain) {{
    const exp = new Date(Date.now() + days * 86400000).toUTCString();
    const dp  = domain ? ";domain=" + domain : "";
    document.cookie = name + "=" + value + ";expires=" + exp + ";path=/;SameSite=Lax" + dp;
  }}

  function clearGoogTransCookie() {{
    const exp = "Thu, 01 Jan 1970 00:00:00 GMT";
    getCookieDomains().forEach(function(d) {{
      const dp = d ? ";domain=" + d : "";
      document.cookie = "googtrans=;expires=" + exp + ";path=/" + dp;
      document.cookie = "googtrans=;expires=" + exp + ";path=/" + dp + ";SameSite=Lax";
    }});
  }}

  function setGoogTransCookie(lang) {{
    const n = normalizeLanguage(lang);
    if (n === sourceLang) {{ clearGoogTransCookie(); return; }}
    getCookieDomains().forEach(function(d) {{
      setCookie("googtrans", "/" + sourceLang + "/" + n, 365, d);
    }});
  }}

  // ── SESSION STORAGE ─────────────────────────────────────────
  function getStoredLanguage() {{
    return normalizeLanguage(sessionStorage.getItem(STORAGE_KEY));
  }}

  function setStoredLanguage(lang) {{
    const n = normalizeLanguage(lang);
    sessionStorage.setItem(STORAGE_KEY, n);
    setGoogTransCookie(n);
    return n;
  }}

  // ── OVERLAY ─────────────────────────────────────────────────
  function showOverlay() {{
    var o = document.getElementById("gt-loading-overlay");
    if (o) o.style.display = "flex";
    document.body.classList.add("gt-loading");
    document.body.classList.remove("gt-ready");
  }}

  function hideOverlay() {{
    var o = document.getElementById("gt-loading-overlay");
    document.body.classList.remove("gt-loading");
    document.body.classList.add("gt-ready");
    if (o) {{
      o.classList.add("gt-overlay-hide");
      setTimeout(function() {{ o.style.display = "none"; }}, 400);
    }}
  }}

  // ── СКРИВАНЕ НА GOOGLE BANNER ───────────────────────────────
  function hideGoogleBanner() {{
    document.body.style.top = "0px";
    [
      "iframe.goog-te-banner-frame", ".goog-te-balloon-frame", "#goog-gt-tt",
      ".goog-tooltip", ".VIpgJd-ZVi9od-ORHb-OEVmcd", ".VIpgJd-ZVi9od-l4eHX-hSRGPd",
      ".VIpgJd-yAWNEb-L7lbkb", ".goog-te-spinner-pos", ".goog-te-spinner",
      ".goog-spinner-pos", ".VIpgJd-ZVi9od-aZ2wEe", ".VIpgJd-ZVi9od-aZ2wEe-OiiCO",
      "#goog-wt-spinner"
    ].forEach(function(sel) {{
      document.querySelectorAll(sel).forEach(function(el) {{
        el.style.cssText += ";display:none!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important";
      }});
    }});
  }}

  window.addEventListener("DOMContentLoaded", function() {{
    new MutationObserver(hideGoogleBanner)
      .observe(document.documentElement, {{ childList: true, subtree: true }});
  }});
  setInterval(hideGoogleBanner, 500);

  // ── ОСНОВНА СТРАТЕГИЯ: ПРЕВОД ЧРЕЗ RELOAD ───────────────────
  //
  // При нон-BG език и ново зареждане на страницата:
  //   1. Сетваме googtrans cookie
  //   2. Маркираме в sessionStorage че reload е направен (за този pathname)
  //   3. window.location.reload() → браузърът зарежда страницата наново,
  //      Google Translate чете cookie-то и превежда DOM-а при зареждане.
  //
  // При втора итерация (reload флагът е сетнат):
  //   → просто скриваме overlay-я, преводът вече е в DOM-а.
  //
  // Ключът съдържа pathname → при навигация към нова страница
  // флагът е различен и отново се прави reload → винаги преведено.
  // ────────────────────────────────────────────────────────────
  function applyTranslationViaReload(lang) {{
    if (sessionStorage.getItem(reloadKey()) === "1") {{
      // Reload вече е направен за тази страница — показваме я
      hideOverlay();
      return;
    }}
    // Първо зареждане на тази страница с нон-BG → reload
    showOverlay();
    setGoogTransCookie(lang);
    sessionStorage.setItem(reloadKey(), "1");
    window.location.reload();
  }}

  // ── ИНИЦИАЛИЗАЦИЯ НА ЕЗИК ───────────────────────────────────
  function initializeLanguage() {{
    if (!sessionStorage.getItem(INIT_KEY)) {{
      // Съвсем ново отваряне на сесията → винаги BG
      sessionStorage.setItem(INIT_KEY, "1");
      clearGoogTransCookie();
      return setStoredLanguage(sourceLang);
    }}
    var stored = getStoredLanguage();
    setGoogTransCookie(stored);
    return stored;
  }}

  // ── UI: ЕЗИКОВИ БУТОНИ ──────────────────────────────────────
  function getDisplayName(code, uiLang) {{
    try {{
      if (typeof Intl !== "undefined" && Intl.DisplayNames)
        return new Intl.DisplayNames([uiLang], {{ type: "language" }}).of(code) || code;
    }} catch(e) {{}}
    var f = languages.find(function(l) {{ return l.code === code; }});
    return f ? f.label : code;
  }}

  function getLangLabel(uiLang) {{
    var m = {{ bg:"Избери език / Choose language", en:"Choose language", ru:"Выберите язык", tr:"Dil seç", de:"Sprache wählen" }};
    return m[uiLang] || "Choose language";
  }}

  function renderLanguageOptions(currentLang) {{
    var list  = document.getElementById("lang-list");
    var label = document.getElementById("lang-label");
    if (!list || !label) return;

    var uiLang = normalizeLanguage(currentLang || sourceLang);
    var sorted = languages.slice().sort(function(a, b) {{
      return getDisplayName(a.code, uiLang)
        .localeCompare(getDisplayName(b.code, uiLang), uiLang);
    }});

    label.textContent = getLangLabel(uiLang);
    list.innerHTML = "";

    sorted.forEach(function(lang) {{
      var li  = document.createElement("li");
      var btn = document.createElement("button");
      var fl  = document.createElement("span");
      var nm  = document.createElement("span");

      btn.type = "button";
      btn.className = "lang-item-btn" + (lang.code === uiLang ? " active" : "");
      btn.dataset.lang = lang.code;
      fl.className = "lang-flag";
      fl.textContent = flagMap[lang.code] || "🌐";
      nm.className = "lang-name";
      nm.textContent = getDisplayName(lang.code, uiLang);

      btn.appendChild(fl);
      btn.appendChild(nm);
      li.appendChild(btn);
      list.appendChild(li);

      btn.addEventListener("click", function() {{
        var selected = setStoredLanguage(btn.dataset.lang);

        var widget = document.getElementById("auto-lang-widget");
        var panel  = document.getElementById("lang-panel");
        if (widget) widget.classList.remove("open");
        if (panel)  panel.setAttribute("aria-hidden", "true");

        // Нулираме reload флага при смяна на език —
        // новият избор трябва да тригерира нов reload
        sessionStorage.removeItem(reloadKey());

        if (selected === sourceLang) {{
          clearGoogTransCookie();
          window.location.reload();
        }} else {{
          renderLanguageOptions(selected);
          applyTranslationViaReload(selected);
        }}
      }});
    }});
  }}

  // ── UI: DRAWER TOGGLE ───────────────────────────────────────
  function initWidgetUI() {{
    if (widgetUiInitialized) return;
    var widget = document.getElementById("auto-lang-widget");
    var panel  = document.getElementById("lang-panel");
    var toggle = document.getElementById("lang-drawer-toggle");
    if (!widget || !panel || !toggle) return;

    toggle.addEventListener("click", function() {{
      var isOpen = widget.classList.toggle("open");
      panel.setAttribute("aria-hidden", isOpen ? "false" : "true");
    }});

    document.addEventListener("click", function(e) {{
      if (!widget.contains(e.target)) {{
        widget.classList.remove("open");
        panel.setAttribute("aria-hidden", "true");
      }}
    }});

    widgetUiInitialized = true;
  }}

  // ── GOOGLE TRANSLATE CALLBACK ────────────────────────────────
  // Вика се от Google след като widget-ът се зареди.
  // При reload стратегията DOM-ът вече е преведен от cookie-то —
  // просто инициализираме UI-а и скриваме overlay-я.
  window.googleTranslateElementInit = function() {{
    new google.translate.TranslateElement({{
      pageLanguage: sourceLang,
      includedLanguages: "{included_languages}",
      autoDisplay: false,
    }}, "google_translate_element");

    hideGoogleBanner();
    initWidgetUI();
    renderLanguageOptions(getStoredLanguage());

    var selected = getStoredLanguage();
    if (selected === sourceLang) clearGoogTransCookie();
    hideOverlay();
  }};

  // ── СТАРТИРАНЕ ──────────────────────────────────────────────
  var selectedOnLoad = initializeLanguage();
  initWidgetUI();
  renderLanguageOptions(selectedOnLoad);

  if (selectedOnLoad !== sourceLang) {{
    showOverlay();
    applyTranslationViaReload(selectedOnLoad);
  }} else {{
    document.body.classList.add("gt-ready");
  }}

  // ── PAGESHOW (bfcache — back/forward) ───────────────────────
  // При bfcache restore нулираме reload флага за да се направи
  // нов reload и преводът да се приложи наново.
  window.addEventListener("pageshow", function(e) {{
    if (e.persisted) {{
      sessionStorage.removeItem(reloadKey());
      var selected = getStoredLanguage();
      renderLanguageOptions(selected);
      if (selected !== sourceLang) {{
        applyTranslationViaReload(selected);
      }} else {{
        hideOverlay();
      }}
    }} else {{
      hideOverlay();
      renderLanguageOptions(getStoredLanguage());
    }}
  }});

}})();
</script>

<script src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
"""