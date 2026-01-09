import streamlit as st
import requests
import pandas as pd
import json

# CONFIGURATION
API_URL = "http://localhost:8000"  # Make sure your FastAPI is running here
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
    st.title("📊 Platform Overview")
    
    # Mock Data
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Students", "1,240", "+12%")
    col2.metric("Courses Generated", "8", "+2 this week")
    col3.metric("Quizzes Taken", "8,921", "+5%")
    col4.metric("Avg. Knowledge Gain", "24%", "Pre vs Post")

    st.divider()
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Student Engagement (Last 7 Days)")
        chart_data = pd.DataFrame({
            "Daily Users": [120, 132, 145, 150, 170, 210, 245]
        }, index=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        st.line_chart(chart_data)
    
    with c2:
        st.subheader("Popular Interests")
        st.bar_chart({"Gaming": 45, "Science": 30, "Art": 15, "History": 10})


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
        if st.button("🔍 Research ALL sections", use_container_width=True):
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
        if st.button("✨ Generate drafts for ALL sections", use_container_width=True):
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
        if st.button("💾 Publish ALL drafts", use_container_width=True):
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
            if not draft:
                st.info("No draft loaded yet. Use the buttons above to generate drafts (all at once or per section).")
                continue

            # Prime per-section editor state when a draft arrives
            content_key = f"content_{section_id}"
            quiz_key = f"quiz_{section_id}"
            if content_key not in st.session_state:
                st.session_state[content_key] = draft.get("master_content", "")
            if quiz_key not in st.session_state:
                st.session_state[quiz_key] = json.dumps(draft.get("quiz_data", []), indent=2)

            st.write("---")
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
                            # Keep the draft in state for further tweaks if desired
                        else:
                            st.error("Save failed.")
                    except Exception as e:
                        st.error(f"Invalid JSON in Quiz: {e}")