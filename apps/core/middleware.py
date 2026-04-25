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

        option_tags = "\n".join(
            f'<option value="{code}">{label}</option>' for code, label in languages
        )

        return f"""
<style>
  .goog-te-banner-frame.skiptranslate,
  iframe.goog-te-banner-frame,
  .goog-te-balloon-frame,
  #goog-gt-tt,
  .goog-tooltip,
  .goog-tooltip:hover {{
    display: none !important;
    visibility: hidden !important;
  }}

  body {{
    top: 0 !important;
  }}
</style>
<div id="auto-lang-switcher" style="position:fixed;right:16px;bottom:16px;z-index:99999;background:#fff;padding:10px 12px;border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.15);font-family:Arial,sans-serif;">
  <label for="lang-select" style="display:block;font-size:12px;font-weight:700;margin-bottom:6px;color:#1f2937;">Language</label>
  <select id="lang-select" style="min-width:140px;padding:6px;border:1px solid #d1d5db;border-radius:8px;">
    {option_tags}
  </select>
</div>
<div id="google_translate_element" style="display:none;"></div>
<script>
(function() {{
  const STORAGE_KEY = "varna_site_lang";
  const sourceLang = "bg";

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
    const bannerFrame = document.querySelector("iframe.goog-te-banner-frame");
    if (bannerFrame) {{
      bannerFrame.style.display = "none";
      bannerFrame.style.visibility = "hidden";
    }}
    const tooltip = document.getElementById("goog-gt-tt");
    if (tooltip) {{
      tooltip.style.display = "none";
      tooltip.style.visibility = "hidden";
    }}
  }}

  const bannerObserver = new MutationObserver(hideGoogleTranslateBanner);
  bannerObserver.observe(document.documentElement, {{ childList: true, subtree: true }});
  setInterval(hideGoogleTranslateBanner, 500);

  window.googleTranslateElementInit = function() {{
    new google.translate.TranslateElement({{
      pageLanguage: sourceLang,
      includedLanguages: "bg,en,ru,tr,de",
      autoDisplay: false
    }}, "google_translate_element");

    hideGoogleTranslateBanner();

    const langSelect = document.getElementById("lang-select");
    const selected = getStoredLanguage();
    langSelect.value = selected;

    langSelect.addEventListener("change", function() {{
      setLanguage(langSelect.value);
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