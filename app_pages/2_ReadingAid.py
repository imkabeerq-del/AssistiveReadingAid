from datetime import datetime
import html
import io
import json
import re

import streamlit as st
import streamlit.components.v1 as components

from db import log_activity

SAMPLE_PASSAGES = {
    "Default Sample": (
        "Sample or uncommon word, enter words that of obfuscate, and controls break into "
        "obfuscate of anachronism, aware of its origin, expanding and reading those terms like "
        "obfuscate and anachronism is helpful when working through dense study passages."
    ),
    "Science & Memory": (
        "Neuroplasticity allows the brain to reorganize synaptic connections throughout life. "
        "Structured phonics practice and multisensory reading exercises strengthen phonological awareness "
        "and improve decoding accuracy over time."
    ),
    "Hindi Passage (हिन्दी)": (
        "नियमित रूप से धीरे और स्पष्ट शब्दों में पढ़ने से समझ और आत्मविश्वास दोनों बढ़ते हैं। "
        "कठिन शब्दों को छोटे हिस्सों में बाँटकर पढ़ना आसान और प्रभावी होता है।"
    ),
}

FONT_OPTIONS = {
    "Font Style: Clean Sans": "'Inter', 'Segoe UI', Arial, sans-serif",
    "Font Style: Humanist Sans": "Verdana, Tahoma, 'Segoe UI', sans-serif",
    "Font Style: Readable Serif": "Georgia, 'Palatino Linotype', 'Times New Roman', serif",
    "Font Style: Book Serif": "'Garamond', 'Book Antiqua', Georgia, serif",
    "Font Style: Modern Slab": "'Trebuchet MS', 'Segoe UI', sans-serif",
    "Font Style: Monospace": "'Consolas', 'Courier New', monospace",
}

FONT_SIZES = {
    "Font Size: 16px": 16,
    "Font Size: 18px": 18,
    "Font Size: 20px": 20,
    "Font Size: 22px": 22,
    "Font Size: 24px": 24,
}

WORD_DEFINITIONS = {
    "obfuscate": "uncommon word; break into ob-fus-cate — to make something unclear or harder to grasp",
    "anachronism": "out of its historic time; a thing or detail belonging to a different period",
    "neuroplasticity": "neu-ro-plas-tic-i-ty — the brain's ability to form and adapt neural links",
    "synaptic": "syn-ap-tic — relating to junctions where nerve signals pass between neurons",
    "reorganize": "re-or-ga-nize — to arrange elements into a clearer structure",
    "phonological": "phon-o-log-i-cal — relating to speech sounds and sound patterns in language",
    "multisensory": "mul-ti-sen-so-ry — using sight, sound, and touch together while learning",
    "decoding": "de-cod-ing — turning written letters and syllables into spoken words",
    "expanding": "ex-pand-ing — growing wider in scope, detail, or understanding",
}


def _count_syllables(word: str) -> int:
    cleaned = re.sub(r"[^a-zA-Z]", "", word).lower()
    if not cleaned:
        return 0
    if len(cleaned) <= 3:
        return 1
    cleaned = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", cleaned)
    cleaned = re.sub(r"^y", "", cleaned)
    groups = re.findall(r"[aeiouy]{1,2}", cleaned)
    return max(1, len(groups))


def _analyze_text(text: str) -> dict:
    words = re.findall(r"[\w\u0900-\u097F'-]+", text, flags=re.UNICODE)
    sentences = [s.strip() for s in re.split(r"[.!?।]+", text) if s.strip()]
    word_count = len(words)
    sentence_count = max(1, len(sentences))

    latin_words = [w for w in words if re.search(r"[A-Za-z]", w)]
    easy_count = 0
    medium_count = 0
    high_count = 0
    complex_words: list[str] = []

    for w in words:
        clean_w = re.sub(r"^[^\w\u0900-\u097F]+|[^\w\u0900-\u097F]+$", "", w)
        if not clean_w:
            continue
        if re.search(r"[A-Za-z]", clean_w):
            syls = _count_syllables(clean_w)
            letters = len(re.sub(r"[^A-Za-z]", "", clean_w))
            if syls >= 4 or letters >= 10:
                high_count += 1
                complex_words.append(clean_w)
            elif syls >= 3 or letters >= 7:
                medium_count += 1
                complex_words.append(clean_w)
            else:
                easy_count += 1
        else:
            if len(clean_w) >= 7:
                high_count += 1
                complex_words.append(clean_w)
            elif len(clean_w) >= 5:
                medium_count += 1
                complex_words.append(clean_w)
            else:
                easy_count += 1

    unique_complex = sorted(set(complex_words), key=lambda item: item.lower())

    if latin_words:
        syllable_total = sum(_count_syllables(w) for w in latin_words)
        avg_wps = word_count / sentence_count
        avg_spw = syllable_total / max(1, len(latin_words))
        raw_ease = 206.835 - (1.015 * avg_wps) - (84.6 * avg_spw)
        ease_pct = max(0, min(100, round(raw_ease)))
    else:
        raw_ease = 100 - ((word_count / sentence_count) - 8) * 2.0
        ease_pct = max(15, min(98, round(raw_ease)))

    # 1.0 to 10.0 readability score matching the telemetry card
    readability_score = round(max(1.0, min(10.0, (ease_pct / 10.0))), 1)

    total_classified = max(1, easy_count + medium_count + high_count)
    pointer_pct = max(6, min(94, round(((medium_count * 0.55 + high_count * 1.0) / total_classified) * 100)))

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "ease_pct": ease_pct,
        "readability_score": readability_score,
        "easy_count": easy_count,
        "medium_count": medium_count,
        "high_count": high_count,
        "pointer_pct": pointer_pct,
        "complex_words": unique_complex,
    }


def _build_highlighted_html(text: str, highlight_set: set[str], font_family: str, font_size: int) -> str:
    tokens = re.split(r"(\s+)", text)
    parts = []
    for tok in tokens:
        if not tok:
            continue
        if tok.isspace():
            parts.append(html.escape(tok))
            continue
        plain = re.sub(r"^[^\w\u0900-\u097F]+|[^\w\u0900-\u097F]+$", "", tok).lower()
        if plain and plain in highlight_set:
            parts.append(
                f'<span style="border-bottom:2px solid #EF4444;padding-bottom:1px;color:#F8FAFC;">'
                f"{html.escape(tok)}</span>"
            )
        else:
            parts.append(html.escape(tok))

    return (
        f'<div style="background:#0B0F19;border:1px solid #263244;border-radius:10px;'
        f'padding:14px 16px;font-family:{font_family};font-size:{font_size}px;'
        f'line-height:1.75;color:#CBD5E1;margin-top:8px;margin-bottom:14px;">'
        f'{"".join(parts)}'
        f"</div>"
    )


def _render_telemetry_panel(metrics: dict, selected_word: str) -> None:
    score_val = metrics["readability_score"]
    pointer_pct = metrics["pointer_pct"]
    easy_c = metrics["easy_count"]
    med_c = metrics["medium_count"]
    high_c = metrics["high_count"]

    definition_text = WORD_DEFINITIONS.get(
        selected_word.lower(),
        "break into syllables and read aloud slowly to check pronunciation and context",
    )

    st.markdown(
        f'<div style="background:#101622;border:1px solid #1F2937;border-radius:14px;'
        f'padding:20px 18px;text-align:center;margin-bottom:14px;">'
        f'<div style="font-size:15px;font-weight:600;color:#E2E8F0;margin-bottom:6px;">Readability Score</div>'
        f'<div style="font-size:44px;font-weight:700;color:#F8FAFC;line-height:1.1;margin-bottom:10px;">{score_val:.1f}</div>'
        f'<span style="display:inline-block;background:#1A2234;border:1px solid #2A364D;'
        f'color:#94A3B8;font-size:12px;font-weight:500;padding:3px 12px;border-radius:999px;">Telemetry</span>'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div style="background:#101622;border:1px solid #1F2937;border-radius:14px;'
        f'padding:18px 16px;margin-bottom:14px;">'
        f'<div style="font-size:15px;font-weight:600;color:#E2E8F0;text-align:center;margin-bottom:14px;">Word Difficulty Meter</div>'
        f'<div style="position:relative;padding-bottom:12px;">'
        f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;height:8px;border-radius:999px;overflow:hidden;">'
        f'<div style="background:#22C55E;"></div>'
        f'<div style="background:#EAB308;"></div>'
        f'<div style="background:#EF4444;"></div>'
        f"</div>"
        f'<div style="position:absolute;left:calc({pointer_pct}% - 5px);top:9px;'
        f'width:0;height:0;border-left:5px solid transparent;border-right:5px solid transparent;'
        f'border-bottom:7px solid #F8FAFC;"></div>'
        f"</div>"
        f'<div style="display:flex;justify-content:space-between;gap:6px;margin-top:8px;">'
        f'<span style="background:#1A2234;border:1px solid #263244;color:#CBD5E1;font-size:11.5px;padding:3px 8px;border-radius:999px;">Easy: {easy_c}</span>'
        f'<span style="background:#1A2234;border:1px solid #263244;color:#CBD5E1;font-size:11.5px;padding:3px 8px;border-radius:999px;">Medium: {med_c}</span>'
        f'<span style="background:#1A2234;border:1px solid #263244;color:#CBD5E1;font-size:11.5px;padding:3px 8px;border-radius:999px;">High: {high_c}</span>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div style="background:#101622;border:1px solid #1F2937;border-radius:14px;'
        f'padding:16px;margin-bottom:14px;">'
        f'<div style="font-size:15px;font-weight:600;color:#E2E8F0;margin-bottom:10px;">Interactive Word Details</div>'
        f'<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">'
        f'<span style="background:#1B2436;border:1px solid #2C3A52;color:#F1F5F9;'
        f'font-size:13px;font-weight:600;padding:4px 10px;border-radius:7px;">{html.escape(selected_word)}</span>'
        f'<span style="color:#94A3B8;font-size:13px;line-height:1.45;">{html.escape(definition_text)}</span>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _generate_gtts_audio(text: str, lang_code: str, slow: bool) -> bytes | None:
    try:
        from gtts import gTTS  # type: ignore

        buf = io.BytesIO()
        tts = gTTS(text=text[:1500], lang=lang_code, slow=slow)
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None


def _render_tts_player_bar(text: str, lang_tag: str, gender_choice: str, rate: float) -> None:
    normalized = re.sub(r"\s+", " ", text[:2000]).strip()
    text_js = json.dumps(normalized)
    lang_js = json.dumps(lang_tag)
    want_female_js = "true" if gender_choice == "Female" else "false"
    rate_js = json.dumps(float(rate))

    widget = f"""
    <div style="display:flex;align-items:center;justify-content:flex-end;gap:10px;font-family:Inter,sans-serif;padding:4px 0;">
        <span id="raTtsStatus" style="font-size:12px;color:#8B9BB4;margin-right:auto;"></span>
        <button id="raPlayBtn" type="button" style="background:#4F46E5;color:#FFFFFF;border:none;border-radius:8px;padding:7px 15px;font-size:13px;font-weight:600;cursor:pointer;">
            ▶ Play
        </button>
        <button id="raStopBtn" type="button" style="background:#161F30;color:#E2E8F0;border:1px solid #263244;border-radius:8px;padding:7px 14px;font-size:13px;font-weight:600;cursor:pointer;">
            ■ Stop
        </button>
    </div>
    <script>
    (function() {{
        const synth = window.speechSynthesis;
        const playBtn = document.getElementById("raPlayBtn");
        const stopBtn = document.getElementById("raStopBtn");
        const statusEl = document.getElementById("raTtsStatus");
        const payload = {text_js};
        const lang = {lang_js};
        const wantFemale = {want_female_js};
        const rate = {rate_js};

        function selectVoice() {{
            if (!synth) return null;
            const voices = synth.getVoices() || [];
            if (!voices.length) return null;
            const prefix = lang.split("-")[0].toLowerCase();
            const matches = voices.filter(v => (v.lang || "").toLowerCase().startsWith(prefix));
            const pool = matches.length ? matches : voices;
            const femaleKeys = ["female", "zira", "aria", "samantha", "victoria", "hazel", "heera", "swara", "hindi"];
            const maleKeys = ["male", "david", "mark", "guy", "ravi", "madhur", "daniel"];
            const ranked = pool.map(v => {{
                const n = (v.name || "").toLowerCase();
                let s = (v.lang || "").toLowerCase() === lang.toLowerCase() ? 3 : 0;
                if (wantFemale) {{
                    if (femaleKeys.some(k => n.includes(k))) s += 5;
                    if (maleKeys.some(k => n.includes(k))) s -= 3;
                }} else {{
                    if (maleKeys.some(k => n.includes(k))) s += 5;
                    if (femaleKeys.some(k => n.includes(k))) s -= 3;
                }}
                return {{ v, s }};
            }}).sort((a, b) => b.s - a.s);
            return ranked[0].v;
        }}

        if (playBtn) {{
            playBtn.onclick = function() {{
                if (!synth) {{
                    if (statusEl) statusEl.textContent = "Browser speech unavailable";
                    return;
                }}
                synth.cancel();
                const u = new SpeechSynthesisUtterance(payload);
                u.lang = lang;
                u.rate = rate;
                const chosen = selectVoice();
                if (chosen) u.voice = chosen;
                u.onstart = function() {{ if (statusEl) statusEl.textContent = "Playing (" + lang + ")"; }};
                u.onend = function() {{ if (statusEl) statusEl.textContent = ""; }};
                u.onerror = function() {{ if (statusEl) statusEl.textContent = "Voice unavailable"; }};
                synth.speak(u);
            }};
        }}

        if (stopBtn) {{
            stopBtn.onclick = function() {{
                if (synth) synth.cancel();
                if (statusEl) statusEl.textContent = "Stopped";
            }};
        }}
    }})();
    </script>
    """
    components.html(widget, height=46)


def reading_aid_page() -> None:
    st.session_state.setdefault("reading_aid_text", SAMPLE_PASSAGES["Default Sample"])
    st.session_state.setdefault("reading_history", [])
    st.session_state.setdefault("search_history", [])
    st.session_state.setdefault("ra_snapshot", None)

    st.markdown(
        '<div style="background:#101622;border:1px solid #1F2937;border-radius:14px;padding:20px 22px;">',
        unsafe_allow_html=True,
    )
    st.markdown('<h2 style="margin:0 0 14px 0;">Reading Aid</h2>', unsafe_allow_html=True)

    left_col, right_col = st.columns([2.25, 1], gap="large")

    with left_col:
        c_font, c_size, c_sample = st.columns([1.4, 1.2, 1.1])
        with c_font:
            font_label = st.selectbox("Font Style", list(FONT_OPTIONS.keys()), label_visibility="collapsed", key="ra_font_sel")
        with c_size:
            size_label = st.selectbox("Font Size", list(FONT_SIZES.keys()), index=1, label_visibility="collapsed", key="ra_size_sel")
        with c_sample:
            sample_label = st.selectbox("Sample", list(SAMPLE_PASSAGES.keys()), label_visibility="collapsed", key="ra_sample_sel")

        if st.session_state.get("ra_last_sample") != sample_label:
            st.session_state["ra_last_sample"] = sample_label
            st.session_state["reading_aid_text"] = SAMPLE_PASSAGES[sample_label]

        active_font = FONT_OPTIONS[font_label]
        active_size = FONT_SIZES[size_label]

        st.markdown(
            '<div style="font-size:13.5px;font-weight:600;color:#CBD5E1;margin:12px 0 6px 0;">Enter Text</div>',
            unsafe_allow_html=True,
        )
        entered_text = st.text_area(
            "Enter Text",
            value=st.session_state.get("reading_aid_text", ""),
            height=135,
            label_visibility="collapsed",
            key="ra_input_area",
        )
        st.session_state["reading_aid_text"] = entered_text

        clean_text = entered_text.strip()
        metrics = _analyze_text(clean_text) if clean_text else _analyze_text(SAMPLE_PASSAGES["Default Sample"])

        action_c1, action_c2, action_c3 = st.columns([1.2, 1.2, 1.4])
        with action_c1:
            analyze_clicked = st.button("Analyze Passage", type="primary", use_container_width=True, key="ra_btn_analyze")
        with action_c2:
            lang_choice = st.selectbox("TTS Language", ["English", "Hindi (हिन्दी)"], label_visibility="collapsed", key="ra_tts_lang_sel")
        with action_c3:
            voice_gender = st.selectbox("Voice", ["Female Voice", "Male Voice"], label_visibility="collapsed", key="ra_tts_voice_sel")

        if analyze_clicked and clean_text:
            st.session_state["ra_snapshot"] = {"text": clean_text, "metrics": metrics}
            username = st.session_state.get("username", "User")
            summary = f"Analyzed ({metrics['word_count']} words, Ease {metrics['ease_pct']}%)"
            st.session_state["reading_history"].append({"query": summary, "timestamp": datetime.now().strftime("%I:%M %p")})
            st.session_state["search_history"].append({"query": summary, "timestamp": datetime.now().strftime("%I:%M %p")})
            try:
                log_activity(username, summary)
            except Exception:
                pass

        display_text = clean_text if clean_text else SAMPLE_PASSAGES["Default Sample"]
        highlight_words = set(WORD_DEFINITIONS.keys()) | {w.lower() for w in metrics["complex_words"]}
        st.markdown(
            _build_highlighted_html(display_text, highlight_words, active_font, active_size),
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="font-size:13.5px;font-weight:600;color:#CBD5E1;margin-bottom:8px;">Interactive Word Details</div>',
            unsafe_allow_html=True,
        )
        chips = metrics["complex_words"][:4] if metrics["complex_words"] else ["obfuscate", "anachronism"]
        selected_word = st.selectbox("Inspect word", chips, label_visibility="collapsed", key="ra_word_picker")

        chip_html = []
        for w in chips:
            defn = WORD_DEFINITIONS.get(w.lower(), "break into syllables and read aloud")
            short_def = defn.split("—")[0].strip()
            chip_html.append(
                f'<div style="background:#0B0F19;border:1px solid #263244;border-radius:8px;'
                f'padding:7px 12px;margin-bottom:7px;font-size:12.5px;color:#CBD5E1;">'
                f'<strong style="color:#F8FAFC;">{html.escape(w)}:</strong> {html.escape(short_def)}'
                f"</div>"
            )
        st.markdown("".join(chip_html), unsafe_allow_html=True)

        is_hindi = lang_choice.startswith("Hindi")
        lang_tag = "hi-IN" if is_hindi else "en-US"
        gender_clean = "Female" if voice_gender.startswith("Female") else "Male"
        _render_tts_player_bar(display_text, lang_tag, gender_clean, 0.92)

        if st.button("Generate MP3 Audio", type="secondary", key="ra_mp3_btn"):
            mp3_data = _generate_gtts_audio(display_text, "hi" if is_hindi else "en", slow=True)
            if mp3_data:
                st.audio(io.BytesIO(mp3_data), format="audio/mp3")
            else:
                st.info("Install `gTTS` (`pip install gTTS`) to stream MP3 audio directly in the app.")

    with right_col:
        _render_telemetry_panel(metrics, selected_word)

    st.markdown("</div>", unsafe_allow_html=True)