(function () {
  "use strict";

  const DEFAULT_CONFIG = {
    identity: {
      title: "Vlad Voropaev · Vlad the Cyborg",
      lead: "I like understanding complicated things, building useful tools, and turning what I find into something other people can use.",
      eyebrow: "terminal://public-profile",
    },
    tags: ["AI systems", "local-first tools", "research workflows", "automation"],
    links: [
      { label: "GitHub profile", url: "https://github.com/voropaevv" },
      { label: "local-ai-chat-exporter", url: "https://github.com/voropaevv/local-ai-chat-exporter" },
    ],
    readme: {
      mode: "compact",
      showLeadInsideHero: false,
      height: 360,
      promptMaxLength: 62,
    },
    pages: {
      mode: "interactive",
      showLeadInsidePanel: true,
      promptMaxLength: 96,
    },
    mobile: {
      fallStreamCount: 32,
      cursorSpawnPerFrame: 18,
      promptMaxLength: 48,
    },
    status: {
      mode: "public-profile",
      build: "local-ai-chat-exporter",
      state: "building public utility",
    },
    terminalPrompts: [
      "build local-ai-chat-exporter --target browser",
      "export ai-chats --format markdown,json",
      "index chat-archive --searchable --local-first",
      "package useful-parts --public",
      "prototype small-tool --before system-bloat",
      "publish when-useful --not-before",
    ],
    highlightWords: [
      "VLAD THE CYBORG", "LOCAL FIRST", "AI AGENTS", "CHAT EXPORTER",
      "LOCAL CHAT", "ARCHIVE", "SEARCH", "STRUCTURE", "AUTOMATION", "CODEX",
      "PROTOTYPE", "PUBLIC TOOL", "TOOLS", "GITHUB",
    ],
    cursorDecodeTerms: [
      "LOCAL FIRST", "CHAT EXPORTER", "TOOLS", "CODEX", "AUTOMATION", "STRUCTURE",
    ],
    commandModes: {
      help: "commands: help · project · tools · matrix · github",
      project: "local-ai-chat-exporter: export AI chats into readable local archives",
      tools: "focus: AI systems · local-first tools · research workflows · automation",
      matrix: "matrix intensity boosted",
      github: "opening github profile",
    },
    colors: {
      background: "#000000",
      green: "#00ff41",
      greenDim: "#00451f",
      greenHead: "#c5ffd6",
      cursor: "#eafff0",
      red: "#ff3030",
    },
    animation: {
      wordProbability: 0.84,
      fallStreamCount: 58,
      cursorRadiusPx: 128,
      cursorSpawnPerFrame: 42,
      baseFontSize: 16,
    },
  };

  const GLYPHS_ASCII =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ" +
    "abcdefghijklmnopqrstuvwxyz" +
    "0123456789" +
    "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~\\";

  const GLYPHS_JP_KATAKANA =
    "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンヴガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポァィゥェォャュョッー・";

  const GLYPHS_JP_HIRAGANA =
    "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽぁぃぅぇぉゃゅょっー・";

  const GLYPHS = GLYPHS_ASCII + GLYPHS_JP_KATAKANA + GLYPHS_JP_HIRAGANA;

  const SRC_EMPTY = 0;
  const SRC_BACKGROUND = 1;
  const SRC_CURSOR = 2;
  const SRC_FALLING = 3;
  const SOURCE_PRIORITY = {
    [SRC_EMPTY]: 0,
    [SRC_BACKGROUND]: 1,
    [SRC_CURSOR]: 2,
    [SRC_FALLING]: 3,
  };

  const BG_CFG = {
    SPAWN_INTERVAL_MS: 50,
    SPAWN_COUNT: 10,
    ALPHA_START: 0.2,
    FADE_PER_MS: 0.0005,
  };

  const FALL_CFG = {
    SPEED_SCALE: 0.42,
    MIN_ROWS_PER_SEC: 20,
    MAX_ROWS_PER_SEC: 42,
    MIN_TRAIL: 16,
    MAX_TRAIL: 38,
    HEAD_ALPHA: 1.0,
    TRAIL_ALPHA: 0.82,
    FADE_PER_MS: 0.00045,
  };

  const CURSOR_CFG = {
    ENABLED: true,
    ALPHA_START: 1,
    FADE_PER_MS: 0.0007,
    SIGMA_FRACTION: 0.3,
  };

  const BASE_FONT_SIZE = 16;
  const ROW_GAP_PX = 1;
  const DPR_CAP = 2;

  function mergeConfig(base, override) {
    const out = { ...base, ...override };
    out.identity = { ...base.identity, ...(override.identity || {}) };
    out.colors = { ...base.colors, ...(override.colors || {}) };
    out.animation = { ...base.animation, ...(override.animation || {}) };
    out.readme = { ...base.readme, ...(override.readme || {}) };
    out.pages = { ...base.pages, ...(override.pages || {}) };
    out.mobile = { ...base.mobile, ...(override.mobile || {}) };
    out.status = { ...base.status, ...(override.status || {}) };
    out.commandModes = { ...base.commandModes, ...(override.commandModes || {}) };
    out.tags = override.tags || base.tags;
    out.links = override.links || base.links;
    out.terminalPrompts = override.terminalPrompts || base.terminalPrompts;
    out.highlightWords = override.highlightWords || base.highlightWords;
    out.cursorDecodeTerms = override.cursorDecodeTerms || base.cursorDecodeTerms;
    return out;
  }

  async function loadConfig() {
    try {
      const response = await fetch("matrix.config.json", { cache: "no-store" });
      if (!response.ok) return DEFAULT_CONFIG;
      const remoteConfig = await response.json();
      return mergeConfig(DEFAULT_CONFIG, remoteConfig);
    } catch (_error) {
      return DEFAULT_CONFIG;
    }
  }

  function randInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  function randChoice(str) {
    return str.charAt(Math.floor(Math.random() * str.length));
  }

  function applyTextConfig(config) {
    const titleEl = document.querySelector('[data-config="title"]');
    const leadEl = document.querySelector('[data-config="lead"]');
    const eyebrowEl = document.querySelector('[data-config="eyebrow"]');
    const chipsEl = document.getElementById("chips");
    const linksEl = document.getElementById("links");
    const statusEl = document.getElementById("status-line");

    if (titleEl && config.identity.title) titleEl.textContent = config.identity.title;
    if (leadEl && config.identity.lead) leadEl.textContent = config.identity.lead;
    if (eyebrowEl && config.identity.eyebrow) eyebrowEl.textContent = config.identity.eyebrow;
    if (statusEl && config.status) {
      statusEl.textContent = `mode: ${config.status.mode} · build: ${config.status.build}`;
    }

    if (chipsEl && Array.isArray(config.tags)) {
      chipsEl.innerHTML = "";
      config.tags.forEach((tag) => {
        const span = document.createElement("span");
        span.textContent = tag;
        chipsEl.appendChild(span);
      });
    }

    if (linksEl && Array.isArray(config.links)) {
      linksEl.innerHTML = "";
      config.links.forEach((link) => {
        const anchor = document.createElement("a");
        anchor.href = link.url;
        anchor.textContent = link.label;
        linksEl.appendChild(anchor);
      });
    }
  }

  function startTerminal(config, reducedMotion) {
    const commandEl = document.getElementById("typed-command");
    if (!commandEl) return { showMessage() {} };

    const rawPrompts = Array.isArray(config.terminalPrompts) && config.terminalPrompts.length
      ? config.terminalPrompts
      : DEFAULT_CONFIG.terminalPrompts;
    const promptLimit = window.innerWidth <= 680
      ? Number(config.mobile?.promptMaxLength || DEFAULT_CONFIG.mobile.promptMaxLength)
      : Number(config.pages?.promptMaxLength || DEFAULT_CONFIG.pages.promptMaxLength);
    const prompts = rawPrompts.map((prompt) => prompt.slice(0, promptLimit));

    let forcedUntil = 0;
    let forcedText = "";

    function showMessage(text, durationMs = 2200) {
      forcedText = text;
      forcedUntil = performance.now() + durationMs;
      commandEl.textContent = text;
    }

    if (reducedMotion) {
      commandEl.textContent = prompts[0];
      return { showMessage };
    }

    let promptIndex = 0;
    let charIndex = 0;
    let deleting = false;
    let pauseUntil = 0;

    function tick(now) {
      if (forcedUntil && now < forcedUntil) {
        commandEl.textContent = forcedText;
        window.setTimeout(() => tick(performance.now()), 80);
        return;
      }
      if (forcedUntil) {
        forcedUntil = 0;
        charIndex = 0;
        deleting = false;
      }

      const current = prompts[promptIndex] || "";
      if (pauseUntil && now < pauseUntil) {
        window.setTimeout(() => tick(performance.now()), 80);
        return;
      }
      pauseUntil = 0;

      if (!deleting) {
        charIndex = Math.min(current.length, charIndex + 1);
        commandEl.textContent = current.slice(0, charIndex);
        if (charIndex >= current.length) {
          deleting = true;
          pauseUntil = now + 1300;
        }
      } else {
        charIndex = Math.max(0, charIndex - 2);
        commandEl.textContent = current.slice(0, charIndex);
        if (charIndex <= 0) {
          deleting = false;
          promptIndex = (promptIndex + 1) % prompts.length;
          pauseUntil = now + 280;
        }
      }

      const delay = deleting ? 26 : 42 + Math.random() * 36;
      window.setTimeout(() => tick(performance.now()), delay);
    }

    commandEl.textContent = "";
    tick(performance.now());
    return { showMessage };
  }

  function startMatrix(config, reducedMotion) {
    const canvas = document.getElementById("rain");
    if (!canvas) return { boostRain() {} };

    const ctx = canvas.getContext("2d", { alpha: false });
    const colors = config.colors || DEFAULT_CONFIG.colors;
    const animation = config.animation || DEFAULT_CONFIG.animation;
    const mobile = config.mobile || DEFAULT_CONFIG.mobile;
    const words = Array.isArray(config.highlightWords) ? config.highlightWords : DEFAULT_CONFIG.highlightWords;
    const decodeTerms = Array.isArray(config.cursorDecodeTerms)
      ? config.cursorDecodeTerms
      : DEFAULT_CONFIG.cursorDecodeTerms;
    const wordProbability = Number(animation.wordProbability || DEFAULT_CONFIG.animation.wordProbability);
    let activeFallStreamCount = Number(animation.fallStreamCount || DEFAULT_CONFIG.animation.fallStreamCount);
    let activeCursorRadiusPx = Number(animation.cursorRadiusPx || DEFAULT_CONFIG.animation.cursorRadiusPx);
    let activeCursorSpawnPerFrame = Number(animation.cursorSpawnPerFrame || DEFAULT_CONFIG.animation.cursorSpawnPerFrame);

    let dpr = Math.min(window.devicePixelRatio || 1, DPR_CAP);
    let cssW = 0;
    let cssH = 0;
    let cols = 0;
    let rows = 0;
    let fontSize = 0;
    let rowHeight = 0;
    let grid = [];
    let columns = [];
    let cursorX = 0;
    let cursorY = 0;
    let cursorActive = false;
    let bgSpawnAcc = 0;
    let animationFrameId = 0;
    let lastTs = 0;
    let stopped = false;
    let rainBoostUntil = 0;

    function makeEmptyCell() {
      return { ch: "", alpha: 0, source: SRC_EMPTY, color: colors.green };
    }

    function createGrid() {
      grid = [];
      for (let r = 0; r < rows; r += 1) {
        const rowArr = [];
        for (let c = 0; c < cols; c += 1) {
          rowArr.push(makeEmptyCell());
        }
        grid.push(rowArr);
      }
    }

    function setCell(r, c, ch, alpha, source, color) {
      if (r < 0 || r >= rows || c < 0 || c >= cols) return;
      const cell = grid[r][c];
      if (SOURCE_PRIORITY[source] < SOURCE_PRIORITY[cell.source] && cell.alpha > 0.15) return;
      cell.ch = ch;
      cell.alpha = Math.max(cell.alpha, alpha);
      cell.source = source;
      cell.color = color;
    }

    function pickWord() {
      return words[Math.floor(Math.random() * words.length)] || "";
    }

    function makeColumnState(colIndex) {
      const trailLen = randInt(FALL_CFG.MIN_TRAIL, FALL_CFG.MAX_TRAIL);
      const rowsPerSec =
        (FALL_CFG.MIN_ROWS_PER_SEC + Math.random() * (FALL_CFG.MAX_ROWS_PER_SEC - FALL_CFG.MIN_ROWS_PER_SEC)) *
        FALL_CFG.SPEED_SCALE;
      const wantWord = Math.random() < wordProbability;
      const word = wantWord ? pickWord().replace(/\s+/g, "·") : "";
      const wordStartRow = wantWord ? randInt(0, Math.max(0, rows - 1)) : -1;

      return {
        col: colIndex,
        row: -randInt(0, rows || 1),
        rowsPerMs: rowsPerSec / 1000,
        trail: trailLen,
        acc: 0,
        lastChar: "",
        lastColor: colors.green,
        word,
        wordPos: 0,
        wordStartRow,
      };
    }

    function createColumns() {
      columns = [];
      if (!cols) return;
      const available = Array.from({ length: cols }, (_value, index) => index);
      const count = Math.min(cols, activeFallStreamCount);
      for (let i = 0; i < count; i += 1) {
        const idx = Math.floor(Math.random() * available.length);
        const col = available.splice(idx, 1)[0];
        columns.push(makeColumnState(col));
      }
    }

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, DPR_CAP);
      cssW = Math.max(1, window.innerWidth);
      cssH = Math.max(1, window.innerHeight);
      const isMobile = cssW <= 680;
      activeFallStreamCount = Number(
        isMobile
          ? mobile.fallStreamCount || animation.fallStreamCount || DEFAULT_CONFIG.animation.fallStreamCount
          : animation.fallStreamCount || DEFAULT_CONFIG.animation.fallStreamCount
      );
      activeCursorSpawnPerFrame = Number(
        isMobile
          ? mobile.cursorSpawnPerFrame || animation.cursorSpawnPerFrame || DEFAULT_CONFIG.animation.cursorSpawnPerFrame
          : animation.cursorSpawnPerFrame || DEFAULT_CONFIG.animation.cursorSpawnPerFrame
      );
      activeCursorRadiusPx = Number(animation.cursorRadiusPx || DEFAULT_CONFIG.animation.cursorRadiusPx);
      fontSize = Math.max(13, Math.round(Number(animation.baseFontSize || BASE_FONT_SIZE) * Math.min(1.15, Math.max(0.86, cssW / 1400))));
      rowHeight = fontSize + ROW_GAP_PX;
      cols = Math.ceil(cssW / fontSize);
      rows = Math.ceil(cssH / rowHeight);

      canvas.width = Math.floor(cssW * dpr);
      canvas.height = Math.floor(cssH * dpr);
      canvas.style.width = `${cssW}px`;
      canvas.style.height = `${cssH}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.font = `${fontSize}px ui-monospace, SFMono-Regular, Menlo, Consolas, "Noto Sans CJK JP", monospace`;
      ctx.textBaseline = "top";

      createGrid();
      createColumns();
    }

    function updateBackground(dtMs) {
      bgSpawnAcc += dtMs;
      if (bgSpawnAcc < BG_CFG.SPAWN_INTERVAL_MS) return;
      bgSpawnAcc = 0;

      const spawnCount = performance.now() < rainBoostUntil
        ? BG_CFG.SPAWN_COUNT * 4
        : BG_CFG.SPAWN_COUNT;

      for (let i = 0; i < spawnCount; i += 1) {
        const r = randInt(0, rows - 1);
        const c = randInt(0, cols - 1);
        setCell(r, c, randChoice(GLYPHS), BG_CFG.ALPHA_START, SRC_BACKGROUND, colors.greenDim);
      }
    }

    function updateColumns(dtMs) {
      for (let i = 0; i < columns.length; i += 1) {
        const col = columns[i];
        col.acc += col.rowsPerMs * dtMs;

        while (col.acc >= 1) {
          const prevRow = col.row;
          if (prevRow >= 0 && prevRow < rows && col.lastChar) {
            setCell(prevRow, col.col, col.lastChar, FALL_CFG.TRAIL_ALPHA, SRC_FALLING, col.lastColor);
          }

          col.row += 1;
          const r = col.row;
          let ch;
          let color;
          const isInWord =
            col.word &&
            col.wordStartRow >= 0 &&
            r === col.wordStartRow + col.wordPos &&
            col.wordPos < col.word.length;

          if (isInWord) {
            ch = col.word[col.wordPos];
            color = colors.red;
            col.wordPos += 1;
          } else {
            ch = randChoice(GLYPHS);
            color = colors.green;
          }

          if (r >= 0 && r < rows) {
            setCell(r, col.col, ch, FALL_CFG.HEAD_ALPHA, SRC_FALLING, color === colors.red ? colors.red : colors.greenHead);
          }

          col.lastChar = ch;
          col.lastColor = color;
          col.acc -= 1;

          if (r - col.trail > rows) {
            columns[i] = makeColumnState(col.col);
            break;
          }
        }
      }
    }

    function spawnDecodeWord() {
      if (!decodeTerms.length || Math.random() > 0.16) return;
      const term = decodeTerms[Math.floor(Math.random() * decodeTerms.length)];
      const word = String(term).replace(/\s+/g, "·");
      if (!word) return;

      const startCol = Math.floor(cursorX / fontSize) - Math.floor(word.length / 2);
      const row = Math.floor(cursorY / rowHeight) + randInt(-1, 1);

      for (let i = 0; i < word.length; i += 1) {
        setCell(row, startCol + i, word[i], 0.95, SRC_CURSOR, colors.cursor);
      }
    }

    function updateCursor() {
      if (!CURSOR_CFG.ENABLED || !cursorActive) return;
      const sigma = Math.max(1, activeCursorRadiusPx * CURSOR_CFG.SIGMA_FRACTION);

      spawnDecodeWord();

      for (let i = 0; i < activeCursorSpawnPerFrame; i += 1) {
        const angle = Math.random() * Math.PI * 2;
        const radius = Math.sqrt(Math.random()) * activeCursorRadiusPx;
        const px = cursorX + Math.cos(angle) * radius;
        const py = cursorY + Math.sin(angle) * radius;
        const c = Math.floor(px / fontSize);
        const r = Math.floor(py / rowHeight);
        const distSq = (px - cursorX) ** 2 + (py - cursorY) ** 2;
        const alpha = Math.exp(-distSq / (2 * sigma * sigma)) * CURSOR_CFG.ALPHA_START;
        if (alpha > 0.08) {
          setCell(r, c, randChoice(GLYPHS), alpha, SRC_CURSOR, colors.cursor);
        }
      }
    }

    function fadeCells(dtMs) {
      for (let r = 0; r < rows; r += 1) {
        for (let c = 0; c < cols; c += 1) {
          const cell = grid[r][c];
          if (cell.alpha <= 0) continue;
          const fade = cell.source === SRC_CURSOR
            ? CURSOR_CFG.FADE_PER_MS
            : cell.source === SRC_FALLING
              ? FALL_CFG.FADE_PER_MS
              : BG_CFG.FADE_PER_MS;
          cell.alpha -= fade * dtMs;
          if (cell.alpha <= 0.02) {
            grid[r][c] = makeEmptyCell();
          }
        }
      }
    }

    function draw() {
      ctx.fillStyle = colors.background;
      ctx.fillRect(0, 0, cssW, cssH);
      for (let r = 0; r < rows; r += 1) {
        const y = r * rowHeight;
        for (let c = 0; c < cols; c += 1) {
          const cell = grid[r][c];
          if (!cell.ch || cell.alpha <= 0) continue;
          ctx.globalAlpha = Math.max(0, Math.min(1, cell.alpha));
          ctx.fillStyle = cell.color;
          ctx.fillText(cell.ch, c * fontSize, y);
        }
      }
      ctx.globalAlpha = 1;
    }

    function frame(ts) {
      if (stopped) return;
      const dtMs = lastTs ? Math.min(66, ts - lastTs) : 16;
      lastTs = ts;
      updateBackground(dtMs);
      updateColumns(dtMs);
      updateCursor();
      fadeCells(dtMs);
      draw();
      animationFrameId = window.requestAnimationFrame(frame);
    }

    function renderStatic() {
      updateBackground(500);
      updateColumns(900);
      draw();
    }

    function setCursorFromEvent(event) {
      const touch = event.touches && event.touches.length ? event.touches[0] : event;
      cursorX = touch.clientX;
      cursorY = touch.clientY;
      cursorActive = true;
    }

    function stopLoop() {
      stopped = true;
      if (animationFrameId) window.cancelAnimationFrame(animationFrameId);
      animationFrameId = 0;
    }

    function startLoop() {
      if (reducedMotion) {
        renderStatic();
        return;
      }
      stopped = false;
      lastTs = 0;
      if (!animationFrameId) animationFrameId = window.requestAnimationFrame(frame);
    }

    window.addEventListener("resize", resize, { passive: true });
    window.addEventListener("mousemove", setCursorFromEvent, { passive: true });
    window.addEventListener("touchmove", setCursorFromEvent, { passive: true });
    window.addEventListener("mouseleave", () => { cursorActive = false; }, { passive: true });
    window.addEventListener("touchend", () => { cursorActive = false; }, { passive: true });
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        stopLoop();
      } else {
        startLoop();
      }
    });

    resize();
    startLoop();

    return {
      boostRain(durationMs = 4000) {
        rainBoostUntil = performance.now() + durationMs;
      },
    };
  }

  function setupCommandMode(config, terminalController, matrixController) {
    const modes = config.commandModes || DEFAULT_CONFIG.commandModes;
    const githubUrl = config.identity?.profileUrl || "https://github.com/voropaevv";
    const handledKeys = new Set(["h", "?", "p", "t", "m", "g"]);

    function showMode(name, durationMs = 2600) {
      const message = modes[name] || DEFAULT_CONFIG.commandModes[name] || name;
      terminalController.showMessage(message, durationMs);
    }

    window.addEventListener("keydown", (event) => {
      if (event.metaKey || event.ctrlKey || event.altKey) return;
      const key = event.key.toLowerCase();
      if (!handledKeys.has(key)) return;

      event.preventDefault();

      if (key === "h" || key === "?") {
        showMode("help", 3200);
      } else if (key === "p") {
        showMode("project");
      } else if (key === "t") {
        showMode("tools");
      } else if (key === "m") {
        showMode("matrix");
        matrixController.boostRain(4200);
      } else if (key === "g") {
        showMode("github", 1800);
        window.open(githubUrl, "_blank", "noopener,noreferrer");
      }
    });
  }

  async function main() {
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const config = await loadConfig();
    applyTextConfig(config);
    const terminalController = startTerminal(config, reducedMotion);
    const matrixController = startMatrix(config, reducedMotion);
    setupCommandMode(config, terminalController, matrixController);
  }

  main();
}());
