import streamlit as st

DYSLEXIA_RESOURCES = [
    {
        "name": "International Dyslexia Association (IDA)",
        "url": "https://dyslexiaida.org/",
        "summary": "Research-backed fact sheets, structured literacy guidance, and educational resources for learners and educators.",
    },
    {
        "name": "Yale Center for Dyslexia & Creativity",
        "url": "https://dyslexia.yale.edu/",
        "summary": "Scientific research, neurobiology insights, assistive technology guides, and personal stories.",
    },
    {
        "name": "British Dyslexia Association (BDA)",
        "url": "https://www.bdadyslexia.org.uk/",
        "summary": "Practical reading and writing advice, workplace and study accommodations, and dyslexia-friendly styling guides.",
    },
    {
        "name": "Understood.org — Learning & Attention",
        "url": "https://www.understood.org/en/articles/what-is-dyslexia",
        "summary": "Clear explanations of dyslexia signs, classroom supports, and confidence-building habits.",
    },
    {
        "name": "Made By Dyslexia",
        "url": "https://www.madebydyslexia.org/",
        "summary": "Highlights dyslexic thinking strengths such as spatial reasoning, pattern recognition, and creative problem solving.",
    },
]


def awareness_page() -> None:
    st.title("Understanding Dyslexia")
    st.caption("Awareness, Information & Trusted Learning Resources")

    st.markdown(
        """
        <div class="custom-card">
            <h3>What is Dyslexia?</h3>
            <p class="awareness-description">
                Dyslexia is a specific learning disability that is neurobiological in origin. It is characterized by difficulties
                with accurate and/or fluent word recognition and by poor spelling and decoding abilities.
            </p>
            <p class="awareness-description" style="margin-top:12px;">
                These difficulties typically result from a deficit in the phonological component of language, that is often
                unexpected in relation to other cognitive abilities and the provision of effective classroom instruction.
            </p>
        </div>

        <div class="custom-card">
            <h3>Common Signs and Characteristics</h3>
            <ul>
                <li>Difficulty with reading, especially decoding single words</li>
                <li>Slow and laborious reading</li>
                <li>Problems with spelling</li>
                <li>Avoiding reading aloud</li>
                <li>Difficulty remembering sequences</li>
                <li>Trouble with time management</li>
                <li>Struggling to summarize a story</li>
            </ul>
        </div>

        <div class="custom-card">
            <h3>Key Strengths of Dyslexia</h3>
            <p class="awareness-description">
                While dyslexia presents challenges, many individuals with dyslexia possess significant strengths, often in areas such as:
            </p>
            <ul>
                <li>Creative thinking and problem-solving</li>
                <li>Visual-spatial reasoning</li>
                <li>Seeing the big picture</li>
                <li>Narrative reasoning and storytelling</li>
                <li>High levels of empathy</li>
                <li>Entrepreneurial skills</li>
            </ul>
        </div>

        <div class="custom-card">
            <h3>Support and Accommodations</h3>
            <p class="awareness-description">
                Support is crucial for individuals with dyslexia. Effective strategies include:
            </p>
            <ul>
                <li>Structured Literacy Instruction (Orton-Gillingham approach)</li>
                <li>Assistive Technology (Text-to-speech, speech-to-text)</li>
                <li>Extra time on tests</li>
                <li>Audiobooks and digital reading materials</li>
                <li>Breaking down tasks into smaller steps</li>
                <li>Encouraging strengths and talents</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Official Dyslexia Websites & Further Reading")
    st.caption("Click any link below to open the resource directly in a new browser tab.")

    for res in DYSLEXIA_RESOURCES:
        st.markdown(
            f"""
            <div class="custom-card" style="padding:18px 22px;margin-bottom:14px;">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
                    <div style="max-width:740px;">
                        <h4 style="margin:0 0 4px 0;">{res["name"]}</h4>
                        <p style="margin:0;color:#CBD5E1;font-size:14px;">{res["summary"]}</p>
                    </div>
                    <a href="{res["url"]}" target="_blank" rel="noopener noreferrer"
                       style="background:linear-gradient(135deg,#6366F1 0%,#22D3EE 100%);
                       color:#FFFFFF;text-decoration:none;font-weight:700;font-size:14px;
                       padding:10px 16px;border-radius:10px;white-space:nowrap;">
                        Visit Website
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )