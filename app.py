<style>
    /* Paleta LATAM: Azul escuro, magenta, azul claro, branco e neutros */
    :root {
        --latam-dark: #00306b;
        --latam-primary: #e20674;
        --latam-accent: #00a1e4;
        --latam-bg: #f5f7fa;
        --latam-surface: #ffffff;
        --latam-text: #1f2d3a;
        --latam-muted: #6f7a89;
        --radius: 10px;
        --shadow: 0 8px 20px rgba(0,0,0,0.08);
    }

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: var(--latam-text);
        background: var(--latam-bg);
        margin: 0;
    }

    h1 {
        color: var(--latam-dark);
        text-align: center;
        margin-bottom: 10px;
        font-weight: 700;
    }

    /* Labels de inputs e títulos de seção */
    div[data-testid="stNumberInput"] label,
    div[data-testid="stSelectbox"] label,
    .stMarkdown h3 strong {
        font-weight: 600;
        color: var(--latam-surface) !important;
        font-size: 1.1em;
        margin-bottom: 5px;
    }

    /* Controles (inputs / selectboxes) */
    .stNumberInput, .stSelectbox {
        background-color: var(--latam-dark);
        border-radius: var(--radius);
        padding: 16px;
        margin-bottom: 10px;
        box-shadow: var(--shadow);
        position: relative;
    }

    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] input {
        color: #fff !important;
        background-color: transparent !important;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 6px;
        padding: 10px;
        font-weight: 500;
        outline: none !important;
        box-shadow: none !important;
        caret-color: var(--latam-accent) !important;
    }

    div[data-baseweb="select"] div[role="button"] {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    /* Placeholder / bordas internas mais suaves */
    .stNumberInput .css-1lcbmhc, /* Ajuste genérico caso necessário */
    .stSelectbox .css-1lcbmhc {
        background: transparent;
    }

    /* Botão principal */
    .stButton>button {
        background: linear-gradient(135deg, var(--latam-primary) 0%, var(--latam-accent) 100%);
        color: white;
        border-radius: var(--radius);
        padding: 0.85em 1.6em;
        font-size: 1.1em;
        font-weight: 700;
        width: 100%;
        border: none;
        transition: filter .25s ease, transform .15s ease;
        margin-top: 15px;
        box-shadow: 0 12px 24px rgba(226,6,116,0.35);
    }
    .stButton>button:hover {
        filter: brightness(1.05);
        cursor: pointer;
        transform: translateY(-1px);
    }
    .stButton>button:active {
        transform: translateY(1px);
    }

    /* Alerts (info, warning, error) */
    div[data-testid="stAlert"] {
        border-radius: var(--radius);
        padding: 16px;
        margin-top: 15px;
        font-size: 1.05em;
        font-weight: 600;
        background-color: var(--latam-surface);
        border-left: 6px solid var(--latam-primary);
        color: var(--latam-text);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }
    div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
        color: inherit !important;
    }

    /* Metric destacado */
    [data-testid="stMetric"] {
        background: #f0f8ff;
        padding: 22px;
        border-radius: 14px;
        border: 2px solid var(--latam-accent);
        box-shadow: var(--shadow);
        margin-top: 22px;
        text-align: center;
    }
    [data-testid="stMetric"] label {
        font-size: 1.4em !important;
        color: var(--latam-dark) !important;
        font-weight: 700;
        margin-bottom: 8px;
    }
    [data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 3.5em !important;
        color: var(--latam-primary) !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.08);
    }

    /* Divisores */
    .stDivider {
        margin: 12px 0;
        border-top: 2px solid rgba(0,0,0,0.08);
    }

    /* Parágrafos e títulos */
    .stMarkdown p:last-of-type {
        margin-bottom: 8px;
    }
    .stMarkdown h3 {
        margin-top: 8px;
        margin-bottom: 8px;
        color: var(--latam-dark);
    }

    /* Rodapé */
    .footer {
        text-align: center;
        font-size: 0.9em;
        color: var(--latam-muted);
        margin-top: 3em;
        padding: 24px 0;
        border-top: 1px solid rgba(0,0,0,0.05);
        background: var(--latam-surface);
        border-radius: 6px;
    }

    .linkedin-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background-color: var(--latam-dark);
        color: white !important;
        padding: 0.6em 1.2em;
        border: none;
        border-radius: 5px;
        text-decoration: none;
        font-weight: 600;
        transition: filter .2s ease;
    }
    .linkedin-btn:hover {
        filter: brightness(1.1);
        text-decoration: none;
    }
    .linkedin-icon {
        width: 20px;
        height: 20px;
        fill: white;
    }

    /* Responsividade */
    @media (max-width: 768px) {
        h1 {
            font-size: 2em;
        }

        .stNumberInput, .stSelectbox {
            padding: 12px;
            margin-bottom: 8px;
        }

        .stButton>button {
            padding: 0.65em 1em;
            font-size: 1em;
            margin-top: 12px;
        }

        div[data-testid="stColumns"] {
            flex-direction: column;
        }
        div[data-testid="stColumns"] > div {
            width: 100% !important;
        }

        [data-testid="stMetric"] {
            padding: 16px;
            margin-top: 16px;
        }
        [data-testid="stMetric"] label {
            font-size: 1.1em !important;
        }
        [data-testid="stMetric"] div[data-testid="stMetricValue"] {
            font-size: 2.8em !important;
        }

        .stMarkdown h3 {
            margin-top: 5px;
            margin-bottom: 5px;
        }
        .stMarkdown p:last-of-type {
            margin-bottom: 5px;
        }
    }

    @media (max-width: 480px) {
        h1 {
            font-size: 1.8em;
        }
        .stNumberInput input, .stSelectbox div[data-baseweb="select"] input {
            font-size: 0.9em;
        }
        [data-testid="stMetric"] div[data-testid="stMetricValue"] {
            font-size: 2.2em !important;
        }
    }
</style>
