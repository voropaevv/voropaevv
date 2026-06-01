(function () {
  "use strict";

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

  const WORDS = [
    "VLAD", "VOROPAEV", "VOROPAEVV", "QUESTIONS", "STRANGE", "WHY", "HOW", "WHAT IF",
    "BUILDING", "RESEARCH", "SYSTEMS", "AI AGENTS", "LOCAL AI", "LOCAL FIRST",
    "CHAT EXPORTER", "SOURCE MAP", "CLAIM MATRIX", "MECHANISMS", "EVIDENCE",
    "UNCERTAINTY", "VISUAL STORIES", "DEEP EXPLANATIONS", "EXPLAINERS", "PYTHON",
    "TYPESCRIPT", "COMPUTER VISION", "AUTOMATION", "NOTEBOOKS", "DATA", "DIAGRAMS",
    "SCRIPTS", "PROTOTYPES", "AUDITABLE", "READABLE", "STRUCTURE", "TOOLS", "CODE",
    "GITHUB", "README", "FINDINGS", "BUILD AND SHARE"
  ];

  const COLOR_FALLING = "#00ff41";
  const COLOR_BACKGROUND = "#00451f";
  const COLOR_CURSOR = "#eafff0";
  const COLOR_HEAD_FIRST = "#c5ffd6";
  const COLOR_WORD = "#ff3030";
  const COLOR_BG_FILL = "#000000";

  const WORD_PROBABILITY = 0.86;

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

  const FALL_STREAM_COUNT = 58;

  const CURSOR_CFG = {
    ENABLED: true,
    RADIUS_PX: 128,
    SPAWN_PER_FRAME: 44,
    ALPHA_START: 1,
    FADE_PER_MS: 0.0007,
    SIGMA_FRACTION: 0.3,
  };

  const BASE_FONT_SIZE = 16;
  const ROW_GAP_PX = 1;
  const DPR_CAP = 2;

  const canvas = document.getElementById("rain");
  if (!canvas) return;

  const ctx = canvas.getContext("2d", { alpha: false });
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  let DPR = Math.min(window.devicePixelRatio || 1, DPR_CAP);
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

  function randInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  function randChoice(str) {
    return str.charAt(Math.floor(Math.random() * str.length));
  }

  function pickWord() {
    return WORDS[Math.floor(Math.random() * WORDS.length)] || "";
  }

  function makeEmptyCell() {
    return { ch: "", alpha: 0, source: SRC_EMPTY, color: COLOR_FALLING };
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
    const current = grid[r][c];
    if (SOURCE_PRIORITY[source] < SOURCE_PRIORITY[current.source]) return;
    current.ch = ch;
    current.alpha = alpha;
    current.source = source;
    current.color = color;
  }

  function resize() {
    cssW = window.innerWidth;
    cssH = window.innerHeight;
    DPR = Math.min(window.devicePixelRatio || 1, DPR_CAP);

    canvas.width = Math.floor(cssW * DPR);
    canvas.height = Math.floor(cssH * DPR);
    canvas.style.width = `${cssW}px`;
    canvas.style.height = `${cssH}px`;

    fontSize = Math.max(12, Math.round(BASE_FONT_SIZE * DPR));
    const gap = Math.max(0, Math.round(ROW_GAP_PX * DPR));
    rowHeight = fontSize + gap;

    ctx.font = `${fontSize}px ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace`;
    ctx.textBaseline = "top";

    cols = Math.max(1, Math.floor(canvas.width / fontSize));
    rows = Math.max(1, Math.floor(canvas.height / rowHeight));

    createGrid();
    createColumns();

    ctx.fillStyle = COLOR_BG_FILL;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }

  function createColumns() {
    columns = [];
    const totalStreams = Math.min(cols, FALL_STREAM_COUNT);
    const colIndexes = Array.from({ length: cols }, (_, i) => i);

    for (let i = colIndexes.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [colIndexes[i], colIndexes[j]] = [colIndexes[j], colIndexes[i]];
    }

    const picked = colIndexes.slice(0, totalStreams);
    for (const colIndex of picked) {
      columns.push(makeColumnState(colIndex));
    }
  }

  function makeColumnState(colIndex) {
    const trailLen = randInt(FALL_CFG.MIN_TRAIL, FALL_CFG.MAX_TRAIL);
    const rowsPerSec =
      (FALL_CFG.MIN_ROWS_PER_SEC + Math.random() * (FALL_CFG.MAX_ROWS_PER_SEC - FALL_CFG.MIN_ROWS_PER_SEC)) *
      FALL_CFG.SPEED_SCALE;
    const wantWord = Math.random() < WORD_PROBABILITY;
    const word = wantWord ? pickWord().replace(/\s+/g, "·") : "";
    const wordStartRow = wantWord ? randInt(0, Math.max(0, rows - 1)) : -1;

    return {
      col: colIndex,
      row: -randInt(0, rows),
      rowsPerMs: rowsPerSec / 1000,
      trail: trailLen,
      acc: 0,
      lastChar: "",
      lastColor: COLOR_FALLING,
      word,
      wordPos: 0,
      wordStartRow,
    };
  }

  function updateBackground(dtMs) {
    bgSpawnAcc += dtMs;
    if (bgSpawnAcc < BG_CFG.SPAWN_INTERVAL_MS) return;
    bgSpawnAcc = 0;

    for (let i = 0; i < BG_CFG.SPAWN_COUNT; i += 1) {
      const r = randInt(0, rows - 1);
      const c = randInt(0, cols - 1);
      const ch = randChoice(GLYPHS);
      setCell(r, c, ch, BG_CFG.ALPHA_START, SRC_BACKGROUND, COLOR_BACKGROUND);
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
          color = COLOR_WORD;
          col.wordPos += 1;
        } else {
          ch = randChoice(GLYPHS);
          color = COLOR_FALLING;
        }

        if (r >= 0 && r < rows) {
          setCell(r, col.col, ch, FALL_CFG.HEAD_ALPHA, SRC_FALLING, color === COLOR_WORD ? COLOR_WORD : COLOR_HEAD_FIRST);
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

  function spawnCursorGlyphs() {
    if (!CURSOR_CFG.ENABLED || !cursorActive) return;

    const R = CURSOR_CFG.RADIUS_PX * DPR;
    const sigma = Math.max(1, R * CURSOR_CFG.SIGMA_FRACTION);
    const twoSigma2 = 2 * sigma * sigma;

    for (let i = 0; i < CURSOR_CFG.SPAWN_PER_FRAME; i += 1) {
      const u = Math.random();
      const r = R * Math.sqrt(u);
      const theta = Math.random() * Math.PI * 2;
      const x = cursorX + r * Math.cos(theta);
      const y = cursorY + r * Math.sin(theta);
      const c = Math.floor(x / fontSize);
      const row = Math.floor(y / rowHeight);

      if (c < 0 || c >= cols || row < 0 || row >= rows) continue;

      const alpha0 = Math.exp(-(r * r) / twoSigma2);
      if (alpha0 < 0.05) continue;

      const ch = randChoice(GLYPHS);
      setCell(row, c, ch, CURSOR_CFG.ALPHA_START * alpha0, SRC_CURSOR, COLOR_CURSOR);
    }
  }

  function fadeGrid(dtMs) {
    for (let r = 0; r < rows; r += 1) {
      const rowArr = grid[r];
      for (let c = 0; c < cols; c += 1) {
        const cell = rowArr[c];
        if (cell.alpha <= 0) continue;

        let fadeRate = 0.002;
        if (cell.source === SRC_BACKGROUND) fadeRate = BG_CFG.FADE_PER_MS;
        else if (cell.source === SRC_FALLING) fadeRate = FALL_CFG.FADE_PER_MS;
        else if (cell.source === SRC_CURSOR) fadeRate = CURSOR_CFG.FADE_PER_MS;

        cell.alpha -= fadeRate * dtMs;
        if (cell.alpha <= 0) {
          cell.alpha = 0;
          cell.ch = "";
          cell.source = SRC_EMPTY;
          cell.color = COLOR_FALLING;
        }
      }
    }
  }

  function renderGrid() {
    ctx.fillStyle = COLOR_BG_FILL;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    for (let r = 0; r < rows; r += 1) {
      const y = r * rowHeight;
      const rowArr = grid[r];
      for (let c = 0; c < cols; c += 1) {
        const cell = rowArr[c];
        if (cell.alpha <= 0) continue;
        ctx.globalAlpha = cell.alpha;
        ctx.fillStyle = cell.color;
        ctx.fillText(cell.ch, c * fontSize, y);
      }
    }

    ctx.globalAlpha = 1;
  }

  function drawStaticFrame() {
    updateBackground(1000);
    updateColumns(1000);
    renderGrid();
  }

  let lastTs = performance.now();
  function drawFrame(now) {
    const dtMs = Math.min(50, now - lastTs);
    lastTs = now;

    updateBackground(dtMs);
    updateColumns(dtMs);
    spawnCursorGlyphs();
    fadeGrid(dtMs);
    renderGrid();

    animationFrameId = requestAnimationFrame(drawFrame);
  }

  function stopAnimation() {
    if (!animationFrameId) return;
    cancelAnimationFrame(animationFrameId);
    animationFrameId = 0;
  }

  function startAnimation() {
    if (prefersReducedMotion || document.hidden || animationFrameId) return;
    lastTs = performance.now();
    animationFrameId = requestAnimationFrame(drawFrame);
  }

  function updateCursorFromClient(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    cursorX = (clientX - rect.left) * DPR;
    cursorY = (clientY - rect.top) * DPR;
    cursorActive = true;
  }

  function deactivateCursor() {
    cursorActive = false;
  }

  resize();
  window.addEventListener("resize", resize);
  window.addEventListener("mousemove", (event) => updateCursorFromClient(event.clientX, event.clientY), { passive: true });
  window.addEventListener("mouseleave", deactivateCursor, { passive: true });
  window.addEventListener(
    "touchmove",
    (event) => {
      if (!event.touches || event.touches.length === 0) return;
      const touch = event.touches[0];
      updateCursorFromClient(touch.clientX, touch.clientY);
    },
    { passive: true },
  );
  window.addEventListener("touchend", deactivateCursor, { passive: true });
  window.addEventListener("touchcancel", deactivateCursor, { passive: true });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      deactivateCursor();
      stopAnimation();
    } else {
      startAnimation();
    }
  });

  if (prefersReducedMotion) {
    drawStaticFrame();
    return;
  }

  startAnimation();

  window.addEventListener("pagehide", stopAnimation);
})();
