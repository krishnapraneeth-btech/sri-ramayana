(function () {
  const I18N = window.RAMAYANA_I18N;
  const EPISODES = window.RAMAYANA_EPISODES || [];
  const isAndroid = typeof window.RamayanaNative !== "undefined";

  const state = {
    lang: localStorage.getItem("ramayana_lang") || "te",
    kanda: "all",
    currentEpId: null,
    sceneIdx: 0,
    sceneElapsed: 0,
    isPlaying: false,
    bgmVolume: parseFloat(localStorage.getItem("ramayana_bgm_vol") || "0.55"),
    voiceEnabled: localStorage.getItem("ramayana_voice") !== "false",
    speed: parseFloat(localStorage.getItem("ramayana_speed") || "0.88"),
    subtitlesOn: localStorage.getItem("ramayana_cc") !== "false",
    autoNext: localStorage.getItem("ramayana_autonext") !== "false",
    sentences: [],
    sentenceIdx: -1,
    resumeSentenceIdx: 0,
    ttsSpeaking: false,
    ttsSessionId: 0,
    activeStage: "A",
    currentBgmTrack: null,
    browserAudio: null,
    tickTimer: null,
    progress: JSON.parse(localStorage.getItem("ramayana_progress") || "{}")
  };

  if (!I18N[state.lang]) state.lang = "en";

  const el = {
    homeLangBar: document.getElementById("homeLangBar"),
    playerLangBar: document.getElementById("playerLangBar"),
    downloadApkLink: document.getElementById("downloadApkLink"),
    homeView: document.getElementById("homeView"),
    playerView: document.getElementById("playerView"),
    kandaTabs: document.getElementById("kandaTabs"),
    episodesGrid: document.getElementById("episodesGrid"),
    stageImgA: document.getElementById("stageImgA"),
    stageImgB: document.getElementById("stageImgB"),
    vfxCanvas: document.getElementById("vfxCanvas"),
    playerEpTitle: document.getElementById("playerEpTitle"),
    playerSceneTitle: document.getElementById("playerSceneTitle"),
    shlokaBox: document.getElementById("shlokaBox"),
    shlokaSa: document.getElementById("shlokaSa"),
    shlokaTr: document.getElementById("shlokaTr"),
    narrationBox: document.getElementById("narrationBox"),
    captionsOverlay: document.getElementById("captionsOverlay"),
    ttsToast: document.getElementById("ttsToast"),
    elapsedTimeTxt: document.getElementById("elapsedTimeTxt"),
    totalTimeTxt: document.getElementById("totalTimeTxt"),
    sceneDots: document.getElementById("sceneDots"),
    playPauseBtn: document.getElementById("playPauseBtn"),
    prevSceneBtn: document.getElementById("prevSceneBtn"),
    nextSceneBtn: document.getElementById("nextSceneBtn"),
    nextEpBtn: document.getElementById("nextEpBtn"),
    backHomeBtn: document.getElementById("backHomeBtn"),
    bgmVolSlider: document.getElementById("bgmVolSlider"),
    voiceToggle: document.getElementById("voiceToggle"),
    speedSelect: document.getElementById("speedSelect"),
    subtitlesToggleBtn: document.getElementById("subtitlesToggleBtn"),
    autoNextToggleBtn: document.getElementById("autoNextToggleBtn"),
    voiceHelpBtn: document.getElementById("voiceHelpBtn"),
    playerVoiceHelpBtn: document.getElementById("playerVoiceHelpBtn"),
    voiceModal: document.getElementById("voiceModal"),
    openTtsSettingsBtn: document.getElementById("openTtsSettingsBtn"),
    closeVoiceModalBtn: document.getElementById("closeVoiceModalBtn")
  };

  if (isAndroid && el.downloadApkLink) {
    el.downloadApkLink.classList.add("hidden");
  }
  if (isAndroid && el.openTtsSettingsBtn) {
    el.openTtsSettingsBtn.classList.remove("hidden");
  }

  const visualizer = new window.RamayanaVisualizer(el.vfxCanvas);

  // Sync UI controls from persisted state
  el.bgmVolSlider.value = Math.round(state.bgmVolume * 100);
  el.voiceToggle.checked = state.voiceEnabled;
  el.speedSelect.value = String(state.speed);
  el.subtitlesToggleBtn.classList.toggle("active", state.subtitlesOn);
  el.captionsOverlay.classList.toggle("hidden", !state.subtitlesOn);
  el.autoNextToggleBtn.classList.toggle("active", state.autoNext);

  function fmtTime(sec) {
    const s = Math.max(0, Math.floor(sec));
    const m = Math.floor(s / 60);
    const r = s % 60;
    return `${String(m).padStart(2, "0")}:${String(r).padStart(2, "0")}`;
  }

  function splitSentences(text) {
    // Split gently across Indic danda (।), English periods, exclamations, questions, semicolons
    const raw = text
      .replace(/([.!?।॥;]+)/g, "$1\n")
      .split("\n")
      .map((s) => s.trim())
      .filter((s) => s.length > 0);
    return raw.length ? raw : [text];
  }

  function applyLocalization() {
    const t = I18N[state.lang];
    document.getElementById("uiAppTitle").textContent = t.appTitle;
    document.getElementById("uiAppSubtitle").textContent = t.appSubtitle;
    document.getElementById("uiHeroTitle").textContent = t.appTitle;
    document.getElementById("uiHeroDesc").textContent = t.heroDesc;
    document.getElementById("uiEpisodesCount").textContent = t.episodesCount;
    document.getElementById("uiVoiceHelpBtn").textContent = t.voiceHelpBtn;
    document.getElementById("uiDownloadApkBtn").textContent = t.downloadApkBtn;
    document.getElementById("uiBackToLib").textContent = t.backToLibrary;
    document.getElementById("uiBgmLabel").textContent = t.bgmLabel;
    document.getElementById("uiVoiceLabel").textContent = t.voiceLabel;
    document.getElementById("uiSpeedLabel").textContent = t.speedLabel;
    document.getElementById("uiModalTitle").textContent = t.ttsNoticeTitle;
    document.getElementById("uiModalDesc").textContent = t.voiceHelpDesc;
    document.getElementById("uiOpenTtsBtn").textContent = t.openTtsSettings;
    document.getElementById("closeVoiceModalBtn").textContent = t.closeLabel;
    el.nextEpBtn.textContent = `${t.nextEpisode} ⏩`;

    // Sync active language pills
    document.querySelectorAll(".lang-pill").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.lang === state.lang);
    });

    renderKandaTabs();
    renderEpisodesGrid();
    if (state.currentEpId !== null) {
      updatePlayerSceneUI(false);
    }
  }

  function renderKandaTabs() {
    const t = I18N[state.lang];
    const order = ["all", "bala", "ayodhya", "aranya", "kishkindha", "sundara", "yuddha", "uttara"];
    el.kandaTabs.innerHTML = "";
    order.forEach((key) => {
      const btn = document.createElement("button");
      btn.className = "kanda-tab" + (state.kanda === key ? " active" : "");
      btn.textContent = t.kandas[key];
      btn.onclick = () => {
        state.kanda = key;
        renderKandaTabs();
        renderEpisodesGrid();
      };
      el.kandaTabs.appendChild(btn);
    });
  }

  function renderEpisodesGrid() {
    const t = I18N[state.lang];
    const list = state.kanda === "all" ? EPISODES : EPISODES.filter((e) => e.kanda === state.kanda);
    el.episodesGrid.innerHTML = "";

    list.forEach((ep) => {
      const prog = state.progress[ep.id];
      const pct = prog ? Math.min(100, Math.round(((prog.sceneIdx * 75 + prog.sceneElapsed) / ep.durationSec) * 100)) : 0;
      const card = document.createElement("article");
      card.className = "ep-card";
      card.innerHTML = `
        <div class="ep-thumb-wrap">
          <img class="ep-thumb" src="${ep.cover}" alt="${ep.title[state.lang]}" loading="lazy" />
          <span class="ep-kanda-tag">${t.kandas[ep.kanda]}</span>
          <span class="ep-dur-tag">${t.minutesLabel} • ${t.scenesLabel}</span>
          ${pct > 0 ? `<div class="ep-prog-bar" style="width:${pct}%"></div>` : ""}
        </div>
        <div class="ep-body">
          <h3 class="ep-title">${ep.title[state.lang]}</h3>
          <p class="ep-summary">${ep.summary[state.lang]}</p>
          <button class="ep-play-btn">▶ ${pct > 2 && pct < 98 ? t.resumeEpisode : t.playEpisode}</button>
        </div>
      `;
      card.onclick = () => openEpisode(ep.id, prog && pct < 98 ? prog.sceneIdx : 0);
      el.episodesGrid.appendChild(card);
    });
  }

  function getCurrentEpisode() {
    return EPISODES.find((e) => e.id === state.currentEpId) || EPISODES[0];
  }

  function openEpisode(epId, startSceneIdx = 0) {
    state.currentEpId = epId;
    state.sceneIdx = Math.max(0, Math.min(11, startSceneIdx));
    state.sceneElapsed = 0;
    el.playerView.classList.remove("hidden");
    visualizer.resize();
    visualizer.start();

    if (isAndroid) {
      try { window.RamayanaNative.setKeepScreenOn(true); } catch (e) {}
    }

    renderSceneDots();
    loadScene(state.sceneIdx, true);
  }

  function closePlayer() {
    pausePlayback();
    stopBgm();
    visualizer.stop();
    el.playerView.classList.add("hidden");
    state.currentEpId = null;
    if (isAndroid) {
      try { window.RamayanaNative.setKeepScreenOn(false); } catch (e) {}
    }
    renderEpisodesGrid();
  }

  function renderSceneDots() {
    const ep = getCurrentEpisode();
    el.sceneDots.innerHTML = "";
    ep.scenes.forEach((sc, i) => {
      const btn = document.createElement("button");
      btn.className = "scene-dot";
      btn.title = sc.title[state.lang];
      btn.innerHTML = `<div class="scene-dot-fill"></div>`;
      btn.onclick = () => {
        loadScene(i, state.isPlaying);
      };
      el.sceneDots.appendChild(btn);
    });
  }

  function updateTimelineUI() {
    const ep = getCurrentEpisode();
    const totalElapsed = state.sceneIdx * 75 + state.sceneElapsed;
    el.elapsedTimeTxt.textContent = fmtTime(totalElapsed);
    el.totalTimeTxt.textContent = fmtTime(ep.durationSec);

    const dots = el.sceneDots.querySelectorAll(".scene-dot");
    dots.forEach((dot, i) => {
      const fill = dot.querySelector(".scene-dot-fill");
      if (i < state.sceneIdx) {
        dot.classList.add("done");
        fill.style.width = "100%";
      } else if (i === state.sceneIdx) {
        dot.classList.remove("done");
        const pct = Math.min(100, (state.sceneElapsed / 75) * 100);
        fill.style.width = `${pct}%`;
      } else {
        dot.classList.remove("done");
        fill.style.width = "0%";
      }
    });
  }

  function updatePlayerSceneUI(restartStageAnimation = true) {
    const ep = getCurrentEpisode();
    const sc = ep.scenes[state.sceneIdx];
    const t = I18N[state.lang];

    el.playerEpTitle.textContent = ep.title[state.lang];
    el.playerSceneTitle.textContent = `${t.scenePrefix} ${state.sceneIdx + 1} ${t.ofLabel} ${ep.scenes.length} — ${sc.title[state.lang]}`;

    if (sc.shloka) {
      el.shlokaBox.classList.remove("hidden");
      el.shlokaSa.textContent = sc.shloka.sanskrit;
      el.shlokaTr.textContent = sc.shloka.translit;
    } else {
      el.shlokaBox.classList.add("hidden");
    }

    state.sentences = splitSentences(sc.narration[state.lang]);
    el.narrationBox.innerHTML = state.sentences
      .map((s, idx) => `<span class="sentence-span" data-idx="${idx}">${s}</span> `)
      .join("");

    if (restartStageAnimation) {
      const nextStage = state.activeStage === "A" ? el.stageImgB : el.stageImgA;
      const prevStage = state.activeStage === "A" ? el.stageImgA : el.stageImgB;
      nextStage.src = sc.image;
      nextStage.className = `stage-img cam-${sc.camera || "zoom_in"} active`;
      prevStage.classList.remove("active");
      state.activeStage = state.activeStage === "A" ? "B" : "A";

      visualizer.setMode(sc.vfx || "golden_rays");
    }
    updateTimelineUI();
  }

  function highlightSentence(idx) {
    state.sentenceIdx = idx;
    const spans = el.narrationBox.querySelectorAll(".sentence-span");
    spans.forEach((sp, i) => {
      sp.classList.toggle("speaking", i === idx);
      if (i === idx) {
        sp.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    });
  }

  // ==================== BGM ENGINE ====================
  function playBgmTrack(trackName) {
    const effectiveVol = state.ttsSpeaking ? state.bgmVolume * 0.36 : state.bgmVolume;
    if (isAndroid) {
      state.currentBgmTrack = trackName;
      try { window.RamayanaNative.playBgm(trackName, effectiveVol); } catch (e) {}
      return;
    }

    // Browser HTML5 Audio
    if (!state.browserAudio) {
      state.browserAudio = new Audio();
      state.browserAudio.loop = true;
    }
    const desiredSrc = `audio/${trackName}.mp3`;
    if (state.currentBgmTrack !== trackName) {
      state.currentBgmTrack = trackName;
      state.browserAudio.src = desiredSrc;
      state.browserAudio.volume = Math.max(0, Math.min(1, effectiveVol));
      state.browserAudio.play().catch(() => {});
    } else {
      state.browserAudio.volume = Math.max(0, Math.min(1, effectiveVol));
      if (state.browserAudio.paused && state.isPlaying) {
        state.browserAudio.play().catch(() => {});
      }
    }
  }

  function updateBgmDucking() {
    const effectiveVol = state.ttsSpeaking ? state.bgmVolume * 0.36 : state.bgmVolume;
    if (isAndroid) {
      try { window.RamayanaNative.setBgmVolume(effectiveVol); } catch (e) {}
    } else if (state.browserAudio) {
      state.browserAudio.volume = Math.max(0, Math.min(1, effectiveVol));
    }
  }

  function stopBgm() {
    state.currentBgmTrack = null;
    if (isAndroid) {
      try { window.RamayanaNative.stopBgm(); } catch (e) {}
    } else if (state.browserAudio) {
      state.browserAudio.pause();
    }
  }

  // ==================== SPEECH / TTS ENGINE ====================
  function showTtsToast(msg) {
    el.ttsToast.textContent = msg;
    el.ttsToast.classList.remove("hidden");
    clearTimeout(showTtsToast._tid);
    showTtsToast._tid = setTimeout(() => el.ttsToast.classList.add("hidden"), 5200);
  }

  function stopSpeech() {
    state.ttsSessionId++;
    state.ttsSpeaking = false;
    highlightSentence(-1);
    updateBgmDucking();
    if (isAndroid) {
      try { window.RamayanaNative.stopSpeech(); } catch (e) {}
    } else if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
  }

  // Callback invoked from Android MainActivity when utterance finishes
  window.__onAndroidTtsDone = function (sessionId, sentenceIdx) {
    if (sessionId !== state.ttsSessionId || !state.isPlaying) return;
    speakNextSentence(sessionId, sentenceIdx + 1);
  };

  window.__onAndroidTtsError = function (sessionId) {
    if (sessionId !== state.ttsSessionId) return;
    state.ttsSpeaking = false;
    updateBgmDucking();
  };

  function startSceneSpeech(startSentenceIdx = 0) {
    stopSpeech();
    if (!state.voiceEnabled || !state.isPlaying) return;

    const locale = I18N[state.lang].ttsLocale;
    const sessionId = state.ttsSessionId;

    if (isAndroid) {
      let avail = false;
      try { avail = window.RamayanaNative.isLanguageAvailable(locale); } catch (e) {}
      if (!avail) {
        showTtsToast(I18N[state.lang].ttsFallbackNotice);
        return;
      }
      speakNextSentence(sessionId, startSentenceIdx);
      return;
    }

    // Browser Web Speech API fallback
    if (!("speechSynthesis" in window)) {
      showTtsToast(I18N[state.lang].ttsFallbackNotice);
      return;
    }
    const voices = window.speechSynthesis.getVoices();
    const langPrefix = state.lang;
    const match = voices.find((v) => v.lang.toLowerCase().startsWith(langPrefix));
    if (voices.length > 0 && !match && langPrefix !== "en") {
      showTtsToast(I18N[state.lang].ttsFallbackNotice);
    }
    speakNextSentence(sessionId, startSentenceIdx);
  }

  function speakNextSentence(sessionId, idx) {
    if (sessionId !== state.ttsSessionId || !state.isPlaying || !state.voiceEnabled) return;
    if (idx >= state.sentences.length) {
      state.ttsSpeaking = false;
      state.resumeSentenceIdx = state.sentences.length;
      highlightSentence(-1);
      updateBgmDucking();
      return;
    }

    const sentence = state.sentences[idx];
    const locale = I18N[state.lang].ttsLocale;
    state.ttsSpeaking = true;
    state.resumeSentenceIdx = idx;
    highlightSentence(idx);
    updateBgmDucking();

    if (isAndroid) {
      try {
        window.RamayanaNative.speak(sentence, locale, state.speed, sessionId, idx);
      } catch (e) {
        state.ttsSpeaking = false;
        updateBgmDucking();
      }
      return;
    }

    try {
      const utter = new SpeechSynthesisUtterance(sentence);
      utter.lang = locale;
      utter.rate = state.speed;
      const voices = window.speechSynthesis.getVoices();
      const matched = voices.find((v) => v.lang.toLowerCase() === locale.toLowerCase())
        || voices.find((v) => v.lang.toLowerCase().startsWith(state.lang));
      if (matched) utter.voice = matched;
      utter.onend = () => {
        if (sessionId === state.ttsSessionId && state.isPlaying) {
          speakNextSentence(sessionId, idx + 1);
        }
      };
      utter.onerror = () => {
        if (sessionId === state.ttsSessionId) {
          state.ttsSpeaking = false;
          updateBgmDucking();
        }
      };
      window.speechSynthesis.speak(utter);
    } catch (e) {
      state.ttsSpeaking = false;
      updateBgmDucking();
    }
  }

  // ==================== SCENE & 15-MIN CLOCK CONTROLLER ====================
  function loadScene(idx, autoPlay) {
    const ep = getCurrentEpisode();
    if (idx < 0) idx = 0;
    if (idx >= ep.scenes.length) {
      onEpisodeComplete();
      return;
    }
    state.sceneIdx = idx;
    state.sceneElapsed = 0;
    state.resumeSentenceIdx = 0;
    saveProgress();
    updatePlayerSceneUI(true);

    if (autoPlay) {
      startPlayback();
    } else {
      pausePlayback();
    }
  }

  function startPlayback() {
    const ep = getCurrentEpisode();
    const sc = ep.scenes[state.sceneIdx];
    state.isPlaying = true;
    el.playPauseBtn.textContent = "⏸";
    visualizer.setPlaying(true);

    playBgmTrack(sc.bgm || "bgm_divine_dawn");
    startSceneSpeech(state.resumeSentenceIdx || 0);

    clearInterval(state.tickTimer);
    state.tickTimer = setInterval(() => {
      if (!state.isPlaying) return;
      state.sceneElapsed += 0.5;
      if (Math.floor(state.sceneElapsed) % 4 === 0) saveProgress();
      updateTimelineUI();

      // Guarantee each scene takes 75s (15 mins per episode) AND never cuts off active narration!
      if (state.sceneElapsed >= sc.durationSec && !state.ttsSpeaking) {
        loadScene(state.sceneIdx + 1, true);
      }
    }, 500);
  }

  function pausePlayback() {
    state.isPlaying = false;
    el.playPauseBtn.textContent = "▶";
    visualizer.setPlaying(false);
    clearInterval(state.tickTimer);
    stopSpeech();
    if (isAndroid) {
      try { window.RamayanaNative.pauseBgm(); } catch (e) {}
    } else if (state.browserAudio) {
      state.browserAudio.pause();
    }
  }

  function onEpisodeComplete() {
    const ep = getCurrentEpisode();
    saveProgress(true);
    const nextEp = EPISODES.find((e) => e.id === ep.id + 1);
    if (state.autoNext && nextEp) {
      openEpisode(nextEp.id, 0);
    } else {
      pausePlayback();
    }
  }

  function saveProgress(completed = false) {
    if (!state.currentEpId) return;
    state.progress[state.currentEpId] = {
      sceneIdx: completed ? 11 : state.sceneIdx,
      sceneElapsed: completed ? 75 : Math.floor(state.sceneElapsed)
    };
    localStorage.setItem("ramayana_progress", JSON.stringify(state.progress));
  }

  window.__onAndroidAppPause = function () {
    if (state.isPlaying) pausePlayback();
  };

  // ==================== EVENT LISTENERS ====================
  function onSelectLang(newLang) {
    if (!I18N[newLang] || state.lang === newLang) return;
    state.lang = newLang;
    state.resumeSentenceIdx = 0;
    localStorage.setItem("ramayana_lang", newLang);
    applyLocalization();
    if (state.currentEpId !== null && state.isPlaying) {
      startSceneSpeech(0);
    }
  }

  document.querySelectorAll(".lang-pill").forEach((btn) => {
    btn.addEventListener("click", () => onSelectLang(btn.dataset.lang));
  });

  el.playPauseBtn.addEventListener("click", () => {
    if (state.isPlaying) pausePlayback();
    else startPlayback();
  });

  el.prevSceneBtn.addEventListener("click", () => {
    loadScene(Math.max(0, state.sceneIdx - 1), state.isPlaying);
  });

  el.nextSceneBtn.addEventListener("click", () => {
    const ep = getCurrentEpisode();
    if (state.sceneIdx + 1 < ep.scenes.length) {
      loadScene(state.sceneIdx + 1, state.isPlaying);
    } else {
      onEpisodeComplete();
    }
  });

  el.nextEpBtn.addEventListener("click", () => {
    const next = EPISODES.find((e) => e.id === state.currentEpId + 1);
    if (next) openEpisode(next.id, 0);
  });

  el.backHomeBtn.addEventListener("click", closePlayer);

  el.bgmVolSlider.addEventListener("input", () => {
    state.bgmVolume = parseInt(el.bgmVolSlider.value, 10) / 100;
    localStorage.setItem("ramayana_bgm_vol", String(state.bgmVolume));
    updateBgmDucking();
  });

  el.voiceToggle.addEventListener("change", () => {
    state.voiceEnabled = el.voiceToggle.checked;
    localStorage.setItem("ramayana_voice", String(state.voiceEnabled));
    if (!state.voiceEnabled) stopSpeech();
    else if (state.isPlaying) startSceneSpeech(0);
  });

  el.speedSelect.addEventListener("change", () => {
    state.speed = parseFloat(el.speedSelect.value);
    localStorage.setItem("ramayana_speed", String(state.speed));
    if (state.isPlaying && state.voiceEnabled) {
      startSceneSpeech(Math.max(0, state.sentenceIdx));
    }
  });

  el.subtitlesToggleBtn.addEventListener("click", () => {
    state.subtitlesOn = !state.subtitlesOn;
    localStorage.setItem("ramayana_cc", String(state.subtitlesOn));
    el.subtitlesToggleBtn.classList.toggle("active", state.subtitlesOn);
    el.captionsOverlay.classList.toggle("hidden", !state.subtitlesOn);
  });

  el.autoNextToggleBtn.addEventListener("click", () => {
    state.autoNext = !state.autoNext;
    localStorage.setItem("ramayana_autonext", String(state.autoNext));
    el.autoNextToggleBtn.classList.toggle("active", state.autoNext);
  });

  // Voice Help Modal
  const openVoiceModal = () => el.voiceModal.classList.remove("hidden");
  const closeVoiceModal = () => el.voiceModal.classList.add("hidden");
  el.voiceHelpBtn.addEventListener("click", openVoiceModal);
  el.playerVoiceHelpBtn.addEventListener("click", openVoiceModal);
  el.closeVoiceModalBtn.addEventListener("click", closeVoiceModal);
  el.openTtsSettingsBtn.addEventListener("click", () => {
    if (isAndroid) {
      try { window.RamayanaNative.openTtsSettings(); } catch (e) {}
    }
  });

  if ("speechSynthesis" in window) {
    window.speechSynthesis.onvoiceschanged = () => {};
  }

  // Initialize!
  applyLocalization();
})();
