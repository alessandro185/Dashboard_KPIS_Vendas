import json
from pathlib import Path

root = Path(__file__).resolve().parent

app_code = (root / "kpi-dashboard" / "app.py").read_text(encoding="utf-8")
cleaning_code = (root / "kpi-dashboard" / "data_cleaning.py").read_text(encoding="utf-8")
source_code = (root / "kpi-dashboard" / "data_source.py").read_text(encoding="utf-8")

html = f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <title>Dashboard de KPIs - Vendas</title>
    <meta name="description" content="Dashboard interativo em Python e Streamlit para acompanhamento de KPIs de vendas." />
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📊</text></svg>">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@stlite/browser@1.11.0/build/stlite.css" />
    <style>
      * {{
        box-sizing: border-box;
      }}
      body, html {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        background-color: #0e1117;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        overflow: hidden;
      }}
      #root {{
        width: 100%;
        height: 100%;
      }}
      #custom-loader {{
        position: fixed;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: radial-gradient(circle at 50% 40%, #161f30 0%, #0e1117 100%);
        color: #f8fafc;
        z-index: 99999;
        transition: opacity 0.5s ease, visibility 0.5s ease;
      }}
      .spinner {{
        width: 52px;
        height: 52px;
        border: 4px solid rgba(255, 255, 255, 0.08);
        border-top-color: #ff4b4b;
        border-radius: 50%;
        animation: spin 0.85s cubic-bezier(0.5, 0.1, 0.5, 0.9) infinite;
        margin-bottom: 22px;
        box-shadow: 0 0 24px rgba(255, 75, 75, 0.25);
      }}
      @keyframes spin {{
        to {{ transform: rotate(360deg); }}
      }}
      .loader-title {{
        font-size: 1.35rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        margin-bottom: 8px;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
      }}
      .loader-desc {{
        font-size: 0.92rem;
        color: #94a3b8;
        max-width: 440px;
        text-align: center;
        line-height: 1.55;
        padding: 0 20px;
      }}
      .loader-badge {{
        margin-top: 18px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 999px;
        font-size: 0.78rem;
        color: #cbd5e1;
      }}
      .loaded #custom-loader {{
        opacity: 0;
        visibility: hidden;
        pointer-events: none;
      }}
    </style>
  </head>
  <body>
    <div id="custom-loader">
      <div class="spinner"></div>
      <div class="loader-title">Carregando Dashboard de Vendas...</div>
      <div class="loader-desc">Inicializando o ambiente Python (Pyodide) e carregando Streamlit via WebAssembly diretamente no seu navegador.</div>
      <div class="loader-badge">⚡ Execução client-side WebAssembly</div>
    </div>

    <div id="root"></div>

    <script type="module">
      import {{ mount }} from "https://cdn.jsdelivr.net/npm/@stlite/browser@1.11.0/build/stlite.js";

      const appCode = {json.dumps(app_code)};
      const cleaningCode = {json.dumps(cleaning_code)};
      const sourceCode = {json.dumps(source_code)};

      const root = document.getElementById("root");

      // Oculta o loader customizado quando o Streamlit renderizar o primeiro elemento
      const observer = new MutationObserver((mutations, obs) => {{
        if (root.children.length > 0) {{
          document.body.classList.add("loaded");
          obs.disconnect();
        }}
      }});
      observer.observe(root, {{ childList: true, subtree: true }});

      try {{
        mount({{
          entrypoint: "app.py",
          files: {{
            "app.py": appCode,
            "data_cleaning.py": cleaningCode,
            "data_source.py": sourceCode
          }},
          requirements: ["pandas", "plotly"]
        }}, root);

        // Fallback para esconder a tela de loading após tempo limite
        setTimeout(() => {{
          document.body.classList.add("loaded");
        }}, 25000);
      }} catch (err) {{
        console.error("Erro ao iniciar stlite:", err);
        const title = document.querySelector(".loader-title");
        const desc = document.querySelector(".loader-desc");
        if (title) title.textContent = "Erro ao iniciar aplicação";
        if (desc) desc.textContent = err.message || String(err);
      }}
    </script>
  </body>
</html>
"""

(root / "index.html").write_text(html, encoding="utf-8")
print(f"index.html gerado com sucesso ({len(html)} bytes)")
