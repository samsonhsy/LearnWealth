import streamlit as st
import requests
import pandas as pd
import json

# CONFIGURATION
API_URL = "https://ctflife-demo.zeabur.app/"
# API_URL = "http://localhost:8000"

RESEARCH_FALLBACK_DOMAINS = [
    "ctflife.com.hk",
    "hkma.gov.hk",
    "ifec.org.hk",
    "mpfa.org.hk",
]
st.set_page_config(page_title="LearnWealth Admin", layout="wide")

# --- HELPER FUNCTIONS ---
def fetch_courses():
    try:
        res = requests.get(f"{API_URL}/course-content/admin/courses")
        if res.status_code == 200:
            return res.json()
    except:
        st.error("Cannot connect to Backend API.")
    return []

def fetch_sections(course_id):
    res = requests.get(f"{API_URL}/course-content/admin/course/{course_id}/sections")
    return res.json() if res.status_code == 200 else []


def fetch_research_domains():
    try:
        res = requests.get(f"{API_URL}/course-content/admin/research-domains")
        if res.status_code == 200:
            return res.json()
    except:
        st.error("Cannot connect to Backend API.")
    return []


def create_research_domain(domain: str, label: str | None = None):
    payload = {"domain": domain, "label": label}
    return requests.post(f"{API_URL}/course-content/admin/research-domains", json=payload)


def delete_research_domain(domain_id: int):
    return requests.delete(f"{API_URL}/course-content/admin/research-domains/{domain_id}")


def set_section_draft(section_id: int, draft: dict):
    """Store a draft for a section and prime Streamlit state for editing."""
    if "section_drafts" not in st.session_state:
        st.session_state["section_drafts"] = {}

    st.session_state["section_drafts"][section_id] = draft
    st.session_state[f"content_{section_id}"] = draft.get("master_content", "")
    st.session_state[f"quiz_{section_id}"] = json.dumps(draft.get("quiz_data", []), indent=2)

# --- SIDEBAR ---
st.sidebar.title("LearnWealth Admin")
page = st.sidebar.radio("Navigation", ["Dashboard", "Course Factory", "Content Studio"])

# DASHBOARD PAGE
if page == "Dashboard":
    st.title("📊 Dashboard")
    st.caption("Prototype KPIs to showcase traction, learning outcomes, and funnel health for investors.")

    # --- TOP-LEVEL KPI CARDS ---
    primary_metrics = [
        ("App Downloads", "3,980", "+240 new"),
        ("Active Students", "1,240", "+12% vs last week"),
        ("Course Completions", "312", "+18%"),
        ("Quiz Accuracy", "79%", "+4 pts"),
    ]

    cols = st.columns(len(primary_metrics))
    for col, (label, value, delta) in zip(cols, primary_metrics):
        col.metric(label, value, delta)

    st.divider()

    # --- GROWTH & ACQUISITION SNAPSHOT ---
    acquisition_cols = st.columns([2, 1])
    with acquisition_cols[0]:
        st.subheader("Acquisition funnel (last 7 days)")
        funnel_index = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        funnel_df = pd.DataFrame(
            {
                "App Downloads": [210, 225, 240, 260, 320, 410, 470],
                "New Signups": [150, 162, 170, 188, 230, 305, 330],
                "Activated Learners": [120, 130, 138, 155, 190, 248, 260],
            },
            index=funnel_index,
        )
        st.area_chart(funnel_df)

    with acquisition_cols[1]:
        st.subheader("Download conversion")
        st.metric("Download → Signup Rate", "71%", "+5 pts")
        st.progress(0.71)
        st.caption("Daily target: 65%")

        channels_df = pd.DataFrame(
            {
                "Channel": ["Play Store", "App Store", "Web Landing", "Campus Reps"],
                "Downloads": [1980, 1225, 480, 295],
                "Conversion": ["42%", "38%", "55%", "61%"],
            }
        )
        st.dataframe(channels_df, width='stretch')

    st.divider()

    # --- LEARNING HEALTH ---
    learning_cols = st.columns([1.5, 1, 1])
    with learning_cols[0]:
        st.subheader("Student Engagement")
        engagement_df = pd.DataFrame(
            {
                "Daily Active Students": [120, 132, 145, 150, 170, 210, 245],
                "Lessons Completed": [80, 88, 102, 110, 129, 160, 185],
            },
            index=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        )
        st.line_chart(engagement_df)

    with learning_cols[1]:
        st.subheader("Top Courses")
        top_courses_df = pd.DataFrame(
            [
                {"Course": "Smart Budgeting", "Avg. Score": "81%", "Completion": "78%"},
                {"Course": "Credit Basics HK", "Avg. Score": "76%", "Completion": "65%"},
                {"Course": "Investing 101", "Avg. Score": "83%", "Completion": "71%"},
                {"Course": "Gen Z Retirement", "Avg. Score": "74%", "Completion": "59%"},
            ]
        )
        st.dataframe(top_courses_df, width="stretch", hide_index=True)

    with learning_cols[2]:
        st.subheader("Download vs. Retention")
        retention_df = pd.DataFrame(
            {
                "Metric": ["30-day retention", "Weekly downloads", "Monthly ARPU"],
                "Value": ["52%", "5.2k", "$18"],
                "Target": ["48%", "4.5k", "$15"],
            }
        )
        st.table(retention_df)

    st.divider()

    st.subheader("Learner Demand & Support Health")
    interest_cols = st.columns([2, 1])
    with interest_cols[0]:
        st.caption("Top content requests from in-app polls")
        content_demand_df = pd.DataFrame(
            [
                {"Topic": "Crypto Safety", "Weekly Requests": 182, "WoW Growth": "+34%"},
                {"Topic": "Student Loans", "Weekly Requests": 156, "WoW Growth": "+18%"},
                {"Topic": "ETF Investing", "Weekly Requests": 139, "WoW Growth": "+12%"},
                {"Topic": "Sustainable Finance", "Weekly Requests": 95, "WoW Growth": "+9%"},
                {"Topic": "Side Hustles", "Weekly Requests": 87, "WoW Growth": "+5%"},
            ]
        )
        st.dataframe(content_demand_df, width="stretch", hide_index=True)

    with interest_cols[1]:
        st.caption("Support automation & escalations")
        support_cards = st.columns(2)
        support_cards[0].metric("Automation deflection", "78%", "+9 pts")
        support_cards[1].metric("Open escalations", "14", "-6 vs last week")

        st.progress(0.62, text="Tickets resolved by tutor agent (goal 60%)")

        


# COURSE FACTORY PAGE(Syllabus Agent)
elif page == "Course Factory":
    st.title("🏗️ Course Factory")
    st.markdown("Use **Syllabus Agent** to brainstorm course structures.")

    # TOPIC INPUT
    with st.form("syllabus_form"):
        topic = st.text_input("Enter Topic Name", placeholder="e.g. Student Credit Cards in Hong Kong")
        submitted = st.form_submit_button("Generate Syllabus")

    # STATE MANAGEMENT
    if "syllabus_draft" not in st.session_state:
        st.session_state["syllabus_draft"] = None

    if submitted and topic:
        with st.spinner("AI is brainstorming structure..."):
            res = requests.post(f"{API_URL}/syllabus/admin/generate-syllabus", params={"topic": topic})
            if res.status_code == 200:
                st.session_state["syllabus_draft"] = res.json()
                st.success("Draft Generated!")
            else:
                st.error("Error generating syllabus.")

    # EDITOR & SAVE
    if st.session_state["syllabus_draft"]:
        st.divider()
        st.subheader("Review & Edit")
        
        draft = st.session_state["syllabus_draft"]
        
        # Course Meta
        c_title = st.text_input("Course Title", draft['course_title'])
        c_desc = st.text_area("Description", draft['course_description'])
        
        # Sections Editor
        st.write("### Sections Plan")
        sections_df = pd.DataFrame(draft['sections'])
        edited_df = st.data_editor(sections_df, num_rows="dynamic", width="stretch")
        
        if st.button("💾 Save to Database"):
            # Construct Payload
            payload = {
                "course_title": c_title,
                "course_description": c_desc,
                "sections": edited_df.to_dict(orient="records")
            }
            res = requests.post(f"{API_URL}/syllabus/admin/create-course", json=payload)
            if res.status_code == 200:
                st.success(f"Course '{c_title}' created successfully!")
                st.session_state["syllabus_draft"] = None # Reset
            else:
                st.error("Failed to save.")

# CONTENT STUDIO PAGE (Research & Author Agents)
elif page == "Content Studio":
    st.title("✍️ Content Studio")
    st.markdown("Use **Research Agent and Author Agent** to research and write 'Master Content'.")

    st.divider()
    with st.expander("Manage research domains", expanded=False):
        st.caption("Control which websites the Research Agent is allowed to scrape. Leaving the list empty falls back to trusted defaults.")
        domains = fetch_research_domains()

        if domains:
            for domain in domains:
                d_col1, d_col2, d_col3 = st.columns([3, 2, 1])
                d_col1.write(domain["domain"])
                d_col2.write(domain.get("label") or "—")
                if d_col3.button("Remove", key=f"remove_domain_{domain['id']}"):
                    res = delete_research_domain(domain["id"])
                    if res.status_code == 204:
                        st.experimental_rerun()
                    else:
                        st.error("Unable to delete domain.")
        else:
            st.info(
                "No custom domains configured. Currently using defaults: "
                + ", ".join(RESEARCH_FALLBACK_DOMAINS)
            )

        with st.form("add_domain_form"):
            st.write("### Add new domain")
            new_domain = st.text_input("Domain", placeholder="hkma.gov.hk", help="Enter just the domain, without https://")
            new_label = st.text_input("Friendly label (optional)")
            add_domain = st.form_submit_button("Add domain")

            if add_domain:
                if not new_domain.strip():
                    st.error("Domain is required.")
                else:
                    res = create_research_domain(new_domain.strip(), new_label.strip() or None)
                    if res.status_code in (200, 201):
                        st.success("Domain saved.")
                        st.experimental_rerun()
                    else:
                        try:
                            detail = res.json().get("detail", "Unable to save domain.")
                        except:
                            detail = "Unable to save domain."
                        st.error(detail)
    
    # 1. SELECT COURSE
    courses = fetch_courses()
    if not courses:
        st.warning("No courses found. Go to Course Factory first.")
        st.stop()
        
    course_options = {c['title']: c['id'] for c in courses}
    selected_course_name = st.selectbox("Select Course", list(course_options.keys()))
    course_id = course_options[selected_course_name]
    
    # 2. SELECT SECTION
    sections = fetch_sections(course_id)
    if not sections:
        st.info("No sections in this course.")
        st.stop()

    # Init multi-section draft state
    if "section_drafts" not in st.session_state:
        st.session_state["section_drafts"] = {}

    st.divider()
    st.subheader("Bulk actions")
    st.caption("Run research and draft generation across every section in this course.")

    bulk_col1, bulk_col2, bulk_col3 = st.columns(3)
    with bulk_col1:
        if st.button("🔍 Research ALL sections", width="stretch"):
            with st.spinner("Scraping for every section..."):
                successes, failures = 0, []
                for s in sections:
                    query = (s.get("key_facts") or {}).get("search_query", s["title"])
                    res = requests.post(f"{API_URL}/course-content/admin/research", params={"topic": query})
                    if res.status_code == 200:
                        successes += 1
                    else:
                        failures.append(s["title"])

                st.success(f"Research triggered for {successes}/{len(sections)} sections.")
                if failures:
                    st.error(f"Failed: {', '.join(failures)}")

    with bulk_col2:
        if st.button("✨ Generate drafts for ALL sections", width="stretch"):
            with st.spinner("Generating drafts for every section..."):
                successes, failures = 0, []
                for s in sections:
                    res = requests.post(f"{API_URL}/course-content/admin/draft-section-content/{s['id']}")
                    if res.status_code == 200:
                        data = res.json().get('data', {})
                        set_section_draft(s["id"], data)
                        successes += 1
                    else:
                        failures.append(s["title"])

                st.success(f"Drafts created for {successes}/{len(sections)} sections.")
                if failures:
                    st.error(f"Failed: {', '.join(failures)}")

    with bulk_col3:
        if st.button("💾 Publish ALL drafts", width="stretch"):
            with st.spinner("Publishing all available drafts..."):
                successes, failures = 0, []
                for s in sections:
                    section_id = s["id"]
                    draft = st.session_state["section_drafts"].get(section_id)
                    if not draft:
                        continue  # skip sections without drafts

                    content_key = f"content_{section_id}"
                    quiz_key = f"quiz_{section_id}"
                    content_val = st.session_state.get(content_key, draft.get("master_content", ""))
                    quiz_text = st.session_state.get(quiz_key, json.dumps(draft.get("quiz_data", [])))

                    try:
                        quiz_data = json.loads(quiz_text)
                        payload = {
                            "master_content": content_val,
                            "quiz_data": quiz_data
                        }
                        res = requests.post(
                            f"{API_URL}/course-content/admin/save-section-content/{section_id}",
                            json=payload
                        )
                        if res.status_code == 200:
                            successes += 1
                        else:
                            failures.append(f"{s['title']} (HTTP {res.status_code})")
                    except Exception as e:
                        failures.append(f"{s['title']} (Invalid quiz JSON: {e})")

                st.success(f"Published {successes} section(s) with drafts.")
                if failures:
                    st.error("Issues: " + ", ".join(failures))

    st.divider()
    st.subheader("Section drafts")
    st.caption("Edit and publish drafts per section. Re-run research/draft on a single section if needed.")

    # Sort sections by order for a predictable UI
    sections_sorted = sorted(sections, key=lambda s: s.get("order_index", 0))

    for section in sections_sorted:
        section_id = section["id"]
        section_title = section["title"]
        order_label = section.get("order_index", "?")
        draft = st.session_state["section_drafts"].get(section_id)

        with st.expander(f"{order_label}. {section_title}", expanded=False):
            if section.get('master_content'):
                st.info("✅ Existing content already published for this section.")
            else:
                st.warning("⚠️ No published content yet.")

            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.button("🔍 Research this section", key=f"research_{section_id}"):
                    with st.spinner("Scraping sources..."):
                        query = (section.get("key_facts") or {}).get("search_query", section_title)
                        res = requests.post(f"{API_URL}/course-content/admin/research", params={"topic": query})
                        if res.status_code == 200:
                            st.success("Research saved to Knowledge Base!")
                        else:
                            st.error("Research failed.")

            with action_col2:
                if st.button("✨ Generate draft", key=f"draft_{section_id}"):
                    with st.spinner("Generating draft..."):
                        res = requests.post(f"{API_URL}/course-content/admin/draft-section-content/{section_id}")
                        if res.status_code == 200:
                            data = res.json().get('data', {})
                            set_section_draft(section_id, data)
                            st.success("Draft created!")
                        else:
                            st.error("Generation failed. Did you run research first?")

            draft = st.session_state["section_drafts"].get(section_id)

            content_key = f"content_{section_id}"
            quiz_key = f"quiz_{section_id}"
            fallback_content = section.get("master_content") or ""
            fallback_quiz = section.get("quiz_data", [])

            if content_key not in st.session_state:
                st.session_state[content_key] = draft.get("master_content", fallback_content) if draft else fallback_content
            if quiz_key not in st.session_state:
                source_quiz = draft.get("quiz_data", fallback_quiz) if draft else fallback_quiz
                st.session_state[quiz_key] = json.dumps(source_quiz, indent=2)

            published_tab, editor_tab = st.tabs(["Published content", "Draft / Editor"])

            with published_tab:
                if fallback_content:
                    st.markdown(fallback_content)
                else:
                    st.info("No published content yet.")

                if fallback_quiz:
                    st.write("### 📚 Published quiz questions")
                    for idx, quiz in enumerate(fallback_quiz, start=1):
                        st.markdown(f"**Q{idx}.** {quiz.get('question')}")
                        options = quiz.get("options") or []
                        if options:
                            st.caption("Options: " + ", ".join(options))
                        st.caption(f"Correct answer: {quiz.get('correct_answer')}")
                else:
                    st.caption("No quiz published yet.")

            with editor_tab:
                if draft:
                    st.caption("Editing the latest AI draft. Publishing will overwrite the live content.")
                else:
                    st.caption("Editing the currently published content. Generate a draft to start from an AI suggestion.")

                with st.form(f"edit_content_form_{section_id}"):
                    st.write("### 📝 Master Content (Neutral)")
                    edited_content = st.text_area(
                        "Tutorial Text",
                        key=content_key,
                        height=200
                    )

                    st.write("### 🧠 Quiz Configuration")
                    edited_quiz_json = st.text_area(
                        "Quiz JSON (Edit Carefully)",
                        key=quiz_key,
                        height=300
                    )

                    save_btn = st.form_submit_button("💾 Publish to App")

                    if save_btn:
                        try:
                            final_quiz_data = json.loads(edited_quiz_json)
                            payload = {
                                "master_content": edited_content,
                                "quiz_data": final_quiz_data
                            }
                            res = requests.post(
                                f"{API_URL}/course-content/admin/save-section-content/{section_id}",
                                json=payload
                            )
                            if res.status_code == 200:
                                st.success("Published successfully! Students can now see this.")
                                st.session_state.pop(content_key, None)
                                st.session_state.pop(quiz_key, None)
                                st.experimental_rerun()
                            else:
                                st.error("Save failed.")
                        except Exception as e:
                            st.error(f"Invalid JSON in Quiz: {e}")