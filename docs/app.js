/* dof-diario · static search and stats over the DOF table of contents.
   No build step and no dependencies: plain ES2020 that runs on GitHub Pages. */
(() => {
  "use strict";

  const I18N = {
    es: {
      "doc.title": "dof-diario · el sumario del Diario Oficial, archivado cada día",
      "nav.search": "Buscar",
      "nav.stats": "Estadísticas",
      "nav.data": "Datos",
      "hero.kicker": "Dataset abierto · actualizado a diario",
      "hero.title": "El sumario del Diario Oficial, <em>archivado cada día.</em>",
      "hero.lede":
        "Cada nota publicada en el <strong>Diario Oficial de la Federación</strong> desde enero de 2025: título, dependencia, edición y liga oficial. Un robot de GitHub Actions lo consulta después de cada edición y guarda lo nuevo en este repositorio.",
      "tile.notes": "notas archivadas",
      "tile.days": "días con edición",
      "tile.agencies": "dependencias",
      "tile.last": "última edición archivada",
      "search.heading": "Buscar en el sumario",
      "search.label": "Palabras clave",
      "search.placeholder": 'hidrocarburos, "gas natural", NOM | norma…',
      "search.hint":
        'Sin acentos ni mayúsculas: <code>energia</code> encuentra <code>Energía</code>. Las palabras son prefijos (<code>eléctric</code>), usa <code>"comillas"</code> para frases y <code>|</code> para alternativas.',
      "filter.agency": "Dependencia",
      "filter.all": "Todas",
      "filter.edition": "Edición",
      "filter.from": "Desde",
      "filter.to": "Hasta",
      "filter.reset": "Limpiar",
      "ed.matutina": "Matutina",
      "ed.vespertina": "Vespertina",
      "ed.extraordinaria": "Extraordinaria",
      "status.loading": "Cargando el índice…",
      "status.error": "No se pudo cargar el índice. Intenta de nuevo más tarde.",
      "status.count": (n, ms) => `<b>${n}</b> ${n === "1" ? "nota" : "notas"} · ${ms} ms`,
      "status.note": "Sin avisos judiciales y generales (SIDOF los titula con un código).",
      "results.more": "Ver más",
      "results.empty": "Sin resultados. Prueba con un prefijo más corto, alternativas con | o un rango más amplio.",
      "results.page": "p.",
      "results.filter": "Filtrar por esta dependencia",
      "stats.heading": "Estadísticas",
      "stats.month": "Notas por mes",
      "stats.monthNote": "Notas con título, sin avisos. Haz clic en un mes para buscarlo.",
      "stats.top": "Dependencias con más publicaciones",
      "stats.topNote": "Sin avisos. Haz clic para filtrar la búsqueda.",
      "stats.bar": (month, n, avisos) => `${month}: ${n} notas y ${avisos} avisos`,
      "stats.partial": "(mes en curso)",
      "data.heading": "Usa los datos",
      "data.day": "Un archivo por día",
      "data.dayNote": "JSON normalizado con cada nota, su dependencia, página y liga oficial.",
      "data.schema": "Esquema documentado",
      "data.schemaNote":
        'Cada archivo cumple el <a href="https://github.com/BEG-lag/dof-diario/blob/main/schema/day.schema.json">JSON Schema</a> y se valida en cada actualización.',
      "data.agent": "Para agentes de IA",
      "data.agentNote":
        'El servidor <a href="https://github.com/BEG-lag/mcp-dof">mcp-dof</a> da a Claude el texto completo de cada nota.',
      "footer.disclaimer":
        "No oficial: solo el DOF impreso/oficial es fuente auténtica; no constituye asesoría legal.",
      "footer.source":
        'Datos obtenidos de la API pública de SIDOF (Secretaría de Gobernación). Proyecto independiente, sin afiliación con el DOF. <a href="https://github.com/BEG-lag/dof-diario">Código y datos en GitHub</a>.',
      "footer.portfolio": "portafolio",
      "lang.other": "EN",
      "lang.label": "Change language to English",
    },
    en: {
      "doc.title": "dof-diario · Mexico's Diario Oficial, archived every day",
      "nav.search": "Search",
      "nav.stats": "Stats",
      "nav.data": "Data",
      "hero.kicker": "Open dataset · updated daily",
      "hero.title": "Mexico's Diario Oficial, <em>archived every day.</em>",
      "hero.lede":
        "Every note published in the <strong>Diario Oficial de la Federación</strong>, Mexico's official gazette, since January 2025: title, issuing agency, edition and official link. A GitHub Actions robot checks after every edition and commits what is new to this repository.",
      "tile.notes": "notes archived",
      "tile.days": "days with an edition",
      "tile.agencies": "issuing agencies",
      "tile.last": "latest edition archived",
      "search.heading": "Search the table of contents",
      "search.label": "Keywords",
      "search.placeholder": 'hidrocarburos, "gas natural", NOM | norma…',
      "search.hint":
        'Accent and case insensitive: <code>energia</code> finds <code>Energía</code>. Words are prefixes (<code>eléctric</code>); use <code>"quotes"</code> for phrases and <code>|</code> for alternatives. Titles are in Spanish.',
      "filter.agency": "Agency",
      "filter.all": "All",
      "filter.edition": "Edition",
      "filter.from": "From",
      "filter.to": "To",
      "filter.reset": "Reset",
      "ed.matutina": "Matutina",
      "ed.vespertina": "Vespertina",
      "ed.extraordinaria": "Extraordinaria",
      "status.loading": "Loading the index…",
      "status.error": "The index could not be loaded. Please try again later.",
      "status.count": (n, ms) => `<b>${n}</b> ${n === "1" ? "note" : "notes"} · ${ms} ms`,
      "status.note": "Avisos judiciales y generales are excluded (SIDOF titles them with a code).",
      "results.more": "Show more",
      "results.empty": "No results. Try a shorter prefix, alternatives with | or a wider date range.",
      "results.page": "p.",
      "results.filter": "Filter by this agency",
      "stats.heading": "Statistics",
      "stats.month": "Notes per month",
      "stats.monthNote": "Titled notes, avisos excluded. Click a month to search it.",
      "stats.top": "Most active issuing agencies",
      "stats.topNote": "Avisos excluded. Click to filter the search.",
      "stats.bar": (month, n, avisos) => `${month}: ${n} notes and ${avisos} avisos`,
      "stats.partial": "(month in progress)",
      "data.heading": "Use the data",
      "data.day": "One file per day",
      "data.dayNote": "Normalized JSON with every note, its agency, page and official link.",
      "data.schema": "Documented schema",
      "data.schemaNote":
        'Every file follows the <a href="https://github.com/BEG-lag/dof-diario/blob/main/schema/day.schema.json">JSON Schema</a> and is validated on each update.',
      "data.agent": "For AI agents",
      "data.agentNote":
        'The <a href="https://github.com/BEG-lag/mcp-dof">mcp-dof</a> server gives Claude the full text of every note.',
      "footer.disclaimer": "Unofficial: only the printed/official DOF is authoritative; not legal advice.",
      "footer.source":
        'Data from the public SIDOF API (Secretaría de Gobernación). Independent project, not affiliated with the DOF. <a href="https://github.com/BEG-lag/dof-diario">Code and data on GitHub</a>.',
      "footer.portfolio": "portfolio",
      "lang.other": "ES",
      "lang.label": "Cambiar el idioma a español",
    },
  };

  const EDITIONS = ["matutina", "vespertina", "extraordinaria"];
  const PAGE = 50;
  const $ = (selector) => document.querySelector(selector);

  const state = {
    lang: "es",
    summary: null,
    notes: [], // {id, date, ed, agency, page, title, folded}
    agencies: [],
    matches: [],
    shown: 0,
    regexes: [],
  };

  // ------------------------------------------------------------------ i18n

  function pickLanguage() {
    const fromUrl = new URLSearchParams(location.search).get("lang");
    if (fromUrl && I18N[fromUrl]) return fromUrl;
    try {
      const saved = localStorage.getItem("dof-diario-lang");
      if (saved && I18N[saved]) return saved;
    } catch (_) {
      /* storage can be blocked; fall through */
    }
    return (navigator.language || "es").toLowerCase().startsWith("es") ? "es" : "en";
  }

  const t = (key) => I18N[state.lang][key] ?? I18N.es[key] ?? key;

  function applyLanguage() {
    document.documentElement.lang = state.lang;
    document.title = t("doc.title");
    document.querySelectorAll("[data-i18n]").forEach((el) => (el.textContent = t(el.dataset.i18n)));
    document.querySelectorAll("[data-i18n-html]").forEach((el) => (el.innerHTML = t(el.dataset.i18nHtml)));
    document
      .querySelectorAll("[data-i18n-placeholder]")
      .forEach((el) => (el.placeholder = t(el.dataset.i18nPlaceholder)));
    const button = $("#lang");
    button.textContent = t("lang.other");
    button.setAttribute("aria-label", t("lang.label"));
    if (state.summary) {
      renderTiles();
      renderCharts();
      renderResults(false);
    }
  }

  // ------------------------------------------------------------- formatting

  const nf = () => new Intl.NumberFormat(state.lang === "es" ? "es-MX" : "en-US");
  const fmtDate = (iso, opts = { day: "numeric", month: "short", year: "numeric" }) =>
    new Intl.DateTimeFormat(state.lang === "es" ? "es-MX" : "en-US", { ...opts, timeZone: "UTC" }).format(
      new Date(`${iso}T12:00:00Z`),
    );
  const escapeHtml = (s) =>
    String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const officialUrl = (id, iso) => {
    const [y, m, d] = iso.split("-");
    return `https://dof.gob.mx/nota_detalle.php?codigo=${id}&fecha=${d}/${m}/${y}`;
  };

  // --------------------------------------------------------------- matching
  // Same semantics as mcp-dof: accent and case insensitive, words are prefixes,
  // "quoted phrases", | (or OR) for alternatives, short ALL-CAPS acronyms are whole words.

  const foldCache = new Map();
  function foldChar(c) {
    let f = foldCache.get(c);
    if (f === undefined) {
      f = c.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().charAt(0) || c;
      foldCache.set(c, f);
    }
    return f;
  }
  // Folding char by char keeps the folded string aligned with the original,
  // so match offsets can be used to highlight the original title.
  const fold = (s) => Array.from(s, foldChar).join("");
  const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  function parseQuery(raw) {
    const alternatives = [];
    for (const chunk of raw.split(/\s*\|\s*|\s+OR\s+/)) {
      const terms = [];
      for (const match of chunk.matchAll(/"([^"]+)"|(\S+)/g)) {
        const token = (match[1] || match[2] || "").trim();
        if (!token) continue;
        const acronym = /^[A-ZÑ0-9]{1,6}$/.test(token) && /[A-ZÑ]/.test(token);
        const body = fold(token).split(/\s+/).map(escapeRe).join("\\s+");
        terms.push(new RegExp(`(?<![\\p{L}\\p{N}])${body}${acronym ? "(?![\\p{L}\\p{N}])" : ""}`, "gu"));
      }
      if (terms.length) alternatives.push(terms);
    }
    return alternatives;
  }

  function matches(note, alternatives) {
    return alternatives.some((terms) =>
      terms.every((re) => {
        re.lastIndex = 0;
        return re.test(note.folded);
      }),
    );
  }

  function highlight(note) {
    const ranges = [];
    for (const re of state.regexes) {
      re.lastIndex = 0;
      for (const m of note.folded.matchAll(re)) ranges.push([m.index, m.index + m[0].length]);
    }
    if (!ranges.length) return escapeHtml(note.title);
    ranges.sort((a, b) => a[0] - b[0]);
    let html = "";
    let cursor = 0;
    for (const [start, end] of ranges) {
      if (start < cursor) continue;
      html += escapeHtml(note.title.slice(cursor, start));
      html += `<mark>${escapeHtml(note.title.slice(start, end))}</mark>`;
      cursor = end;
    }
    return html + escapeHtml(note.title.slice(cursor));
  }

  // ----------------------------------------------------------------- search

  function readForm() {
    return {
      q: $("#q").value.trim(),
      agency: $("#agency").value,
      ed: $("#edition").value,
      from: $("#from").value,
      to: $("#to").value,
    };
  }

  function writeUrl(filters) {
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(filters)) if (value) params.set(key, value);
    if (state.lang !== pickDefaultLang()) params.set("lang", state.lang);
    const query = params.toString();
    history.replaceState(null, "", query ? `?${query}${location.hash}` : location.pathname + location.hash);
  }

  const pickDefaultLang = () => ((navigator.language || "es").toLowerCase().startsWith("es") ? "es" : "en");

  function runSearch() {
    const started = performance.now();
    const filters = readForm();
    const alternatives = filters.q ? parseQuery(filters.q) : [];
    state.regexes = alternatives.flat();
    const agency = filters.agency === "" ? null : Number(filters.agency);
    const ed = filters.ed === "" ? null : Number(filters.ed);
    state.matches = state.notes.filter(
      (note) =>
        (agency === null || note.agency === agency) &&
        (ed === null || note.ed === ed) &&
        (!filters.from || note.date >= filters.from) &&
        (!filters.to || note.date <= filters.to) &&
        (!alternatives.length || matches(note, alternatives)),
    );
    state.elapsed = Math.max(1, Math.round(performance.now() - started));
    state.shown = 0;
    writeUrl(filters);
    renderResults(true);
  }

  function noteHtml(note) {
    const edition = EDITIONS[note.ed];
    const page = note.page ? ` · ${t("results.page")} ${note.page}` : "";
    return `<li class="note">
      <div class="meta">
        <time datetime="${note.date}">${fmtDate(note.date)}</time>
        <span class="badge ${edition}">${t(`ed.${edition}`)}</span>
        <button class="agency-link" type="button" data-agency="${note.agency}" title="${escapeHtml(t("results.filter"))}">${escapeHtml(state.agencies[note.agency])}</button>
        <span class="id">#${note.id}${page}</span>
      </div>
      <h3><a href="${officialUrl(note.id, note.date)}" target="_blank" rel="noopener">${highlight(note)}</a></h3>
    </li>`;
  }

  function renderResults(reset) {
    const list = $("#results");
    if (!state.notes.length) return;
    if (reset || state.shown === 0) {
      state.shown = Math.min(PAGE, state.matches.length);
      list.innerHTML = state.matches.slice(0, state.shown).map(noteHtml).join("");
    } else {
      list.innerHTML = state.matches.slice(0, state.shown).map(noteHtml).join("");
    }
    if (!state.matches.length) list.innerHTML = `<li class="empty">${escapeHtml(t("results.empty"))}</li>`;
    const count = $("#count");
    count.classList.remove("loading");
    count.innerHTML = t("status.count")(nf().format(state.matches.length), state.elapsed ?? 1);
    $("#share").textContent = t("status.note");
    $("#more").hidden = state.shown >= state.matches.length;
  }

  function showMore() {
    const next = Math.min(state.shown + PAGE, state.matches.length);
    $("#results").insertAdjacentHTML("beforeend", state.matches.slice(state.shown, next).map(noteHtml).join(""));
    state.shown = next;
    $("#more").hidden = state.shown >= state.matches.length;
  }

  // ------------------------------------------------------------ stats/tiles

  function renderTiles() {
    const s = state.summary;
    $("#t-notes").textContent = nf().format(s.notes);
    $("#t-days").textContent = nf().format(s.days_with_publications);
    $("#t-agencies").textContent = nf().format(s.agencies_count);
    $("#t-last").textContent = fmtDate(s.last_publication);
  }

  function renderCharts() {
    renderMonths();
    renderTopAgencies();
  }

  function niceMax(value) {
    const step = 10 ** Math.floor(Math.log10(value));
    return Math.ceil(value / step) * step;
  }

  function renderMonths() {
    const months = state.summary.by_month;
    const width = 640;
    const height = 220;
    const pad = { top: 10, right: 6, bottom: 28, left: 34 };
    const max = niceMax(Math.max(...months.map((m) => m.notes)));
    const innerW = width - pad.left - pad.right;
    const innerH = height - pad.top - pad.bottom;
    const slot = innerW / months.length;
    const barW = Math.max(4, slot * 0.68);
    const y = (v) => pad.top + innerH - (v / max) * innerH;
    let svg = `<svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">`;
    for (let i = 0; i <= 4; i++) {
      const value = (max / 4) * i;
      svg += `<line class="gridline" x1="${pad.left}" x2="${width - pad.right}" y1="${y(value)}" y2="${y(value)}"/>`;
      svg += `<text x="${pad.left - 6}" y="${y(value) + 3}" text-anchor="end">${nf().format(value)}</text>`;
    }
    const current = new Date().toISOString().slice(0, 7);
    months.forEach((m, i) => {
      const x = pad.left + slot * i + (slot - barW) / 2;
      const partial = m.month === current;
      const label =
        fmtDate(`${m.month}-01`, { month: "short", year: "numeric" }) + (partial ? ` ${t("stats.partial")}` : "");
      svg += `<g class="month" data-month="${m.month}" style="cursor:pointer">`;
      svg += `<rect x="${pad.left + slot * i}" y="${pad.top}" width="${slot}" height="${innerH}" fill="transparent"/>`;
      svg += `<rect class="bar${partial ? " partial" : ""}" x="${x}" y="${y(m.notes)}" width="${barW}" height="${pad.top + innerH - y(m.notes)}" rx="2"/>`;
      svg += `<title>${escapeHtml(t("stats.bar")(label, nf().format(m.notes), nf().format(m.avisos)))}</title></g>`;
      if (i % 3 === 0) {
        const short = fmtDate(`${m.month}-01`, { month: "short", year: "2-digit" });
        svg += `<text x="${x + barW / 2}" y="${height - 8}" text-anchor="middle">${escapeHtml(short)}</text>`;
      }
    });
    svg += "</svg>";
    const box = $("#by-month");
    box.innerHTML = svg;
    box.setAttribute("aria-label", t("stats.month"));
  }

  function renderTopAgencies() {
    const top = state.summary.top_agencies;
    const max = top[0]?.notes || 1;
    $("#top-agencies").innerHTML = top
      .map(
        (a) => `<li><button type="button" data-agency-name="${escapeHtml(a.name)}">
          <span class="name" title="${escapeHtml(a.name)}">${escapeHtml(a.name)}</span>
          <span class="count">${nf().format(a.notes)}</span>
          <span class="track"><span class="fill" style="width:${((a.notes / max) * 100).toFixed(1)}%"></span></span>
        </button></li>`,
      )
      .join("");
  }

  // ------------------------------------------------------------------- load

  function buildIndex(parts) {
    const names = new Map();
    const agencies = [];
    const counts = [];
    const notes = [];
    for (const part of parts) {
      const local = part.agencies.map((name) => {
        if (!names.has(name)) {
          names.set(name, agencies.length);
          agencies.push(name);
          counts.push(0);
        }
        return names.get(name);
      });
      for (const [id, date, ed, agency, page, title] of part.notes) {
        const a = local[agency];
        counts[a] += 1;
        notes.push({ id, date, ed, agency: a, page, title, folded: fold(title) });
      }
    }
    notes.sort((x, y) => (x.date === y.date ? y.id - x.id : x.date < y.date ? 1 : -1));
    state.notes = notes;
    state.agencies = agencies;
    const select = $("#agency");
    const options = agencies
      .map((name, i) => ({ name, i, n: counts[i] }))
      .sort((x, y) => x.name.localeCompare(y.name, "es"))
      .map((a) => `<option value="${a.i}">${escapeHtml(a.name)} (${a.n})</option>`)
      .join("");
    select.insertAdjacentHTML("beforeend", options);
  }

  function restoreFromUrl() {
    const params = new URLSearchParams(location.search);
    $("#q").value = params.get("q") || "";
    $("#edition").value = params.get("ed") || "";
    $("#from").value = params.get("from") || "";
    $("#to").value = params.get("to") || "";
    const agency = params.get("agency");
    if (agency && $(`#agency option[value="${CSS.escape(agency)}"]`)) $("#agency").value = agency;
  }

  function scrollToSearch() {
    $("#buscar").scrollIntoView({ block: "start" });
  }

  function wireEvents() {
    let timer;
    const debounced = () => {
      clearTimeout(timer);
      timer = setTimeout(runSearch, 120);
    };
    $("#q").addEventListener("input", debounced);
    for (const id of ["#agency", "#edition", "#from", "#to"]) $(id).addEventListener("change", runSearch);
    $("#search-form").addEventListener("submit", (event) => {
      event.preventDefault();
      runSearch();
    });
    $("#search-form").addEventListener("reset", () => setTimeout(runSearch, 0));
    $("#more").addEventListener("click", showMore);
    $("#results").addEventListener("click", (event) => {
      const button = event.target.closest("[data-agency]");
      if (!button) return;
      $("#agency").value = button.dataset.agency;
      runSearch();
    });
    $("#top-agencies").addEventListener("click", (event) => {
      const button = event.target.closest("[data-agency-name]");
      if (!button) return;
      const index = state.agencies.indexOf(button.dataset.agencyName);
      if (index < 0) return;
      $("#agency").value = String(index);
      runSearch();
      scrollToSearch();
    });
    $("#by-month").addEventListener("click", (event) => {
      const group = event.target.closest("[data-month]");
      if (!group) return;
      const [y, m] = group.dataset.month.split("-").map(Number);
      const last = new Date(Date.UTC(y, m, 0)).getUTCDate();
      $("#from").value = `${group.dataset.month}-01`;
      $("#to").value = `${group.dataset.month}-${String(last).padStart(2, "0")}`;
      runSearch();
      scrollToSearch();
    });
    $("#lang").addEventListener("click", () => {
      state.lang = state.lang === "es" ? "en" : "es";
      try {
        localStorage.setItem("dof-diario-lang", state.lang);
      } catch (_) {
        /* ignore */
      }
      applyLanguage();
      writeUrl(readForm());
    });
  }

  async function main() {
    state.lang = pickLanguage();
    applyLanguage();
    wireEvents();
    try {
      const summary = await fetch("data/summary.json").then((r) => {
        if (!r.ok) throw new Error(r.statusText);
        return r.json();
      });
      state.summary = summary;
      renderTiles();
      renderCharts();
      const parts = await Promise.all(
        summary.years.map((year) =>
          fetch(`data/index-${year}.json`).then((r) => {
            if (!r.ok) throw new Error(r.statusText);
            return r.json();
          }),
        ),
      );
      buildIndex(parts);
      restoreFromUrl();
      runSearch();
    } catch (error) {
      console.error(error);
      const count = $("#count");
      count.classList.remove("loading");
      count.textContent = t("status.error");
    }
  }

  main();
})();
