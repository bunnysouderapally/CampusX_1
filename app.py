import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import database
import analysis

# Page configuration
st.set_page_config(page_title="CampusFix", page_icon="🛠️", layout="wide")

# Ensure database tables exist
database.create_database()

# Custom CSS matching the original desktop design scheme
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #08111F;
        color: #FFFFFF;
    }
    
    /* Top Header Bar */
    header[data-testid="stHeader"] {
        background-color: #0B1728;
    }
    
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #101C2D;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #1e293b;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #9AA8BA !important;
        font-weight: bold;
        font-size: 0.85rem;
    }
    
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: bold;
    }
    
    /* Top Navigation Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #0B1728;
        padding: 8px 12px;
        border-radius: 8px;
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #D5DEE9;
        font-weight: bold;
        border-radius: 6px;
        padding: 8px 18px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #F59E0B !important;
        color: #162033 !important;
    }
    
    /* Workflow Banner Box */
    .workflow-box {
        background-color: #101C2D;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #F59E0B;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    .workflow-title {
        color: #F59E0B;
        font-weight: bold;
        font-size: 0.9rem;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Top Bar Header Title
st.markdown("<h1 style='color: white; margin: 0; padding-bottom: 10px;'>CampusFix</h1>", unsafe_allow_html=True)

# Top Navigation Tabs (Replaces the sidebar)
tabs = st.tabs(["Dashboard", "Register", "All Tickets", "Maintenance & Status", "Reports"])

CATEGORIES = ["Electrical", "Furniture", "Plumbing", "IT", "Internet", "Cleaning", "AC/Cooling", "Other"]
PRIORITIES = ["Low", "Medium", "High"]
STATUSES = ["Pending", "In Progress", "Resolved"]

# ===================== DASHBOARD =====================
with tabs[0]:
    st.markdown("<h5 style='color: #F59E0B; font-weight: bold; margin-top: 15px;'>CAMPUS MAINTENANCE</h5>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: white; font-weight: bold;'>Complaint & Tracking System</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9AA8BA;'>Report campus maintenance issues, track their status and analyze repair activity.</p>", unsafe_allow_html=True)
    
    report = analysis.get_report_data()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("TOTAL COMPLAINTS", report["total"])
    col2.metric("PENDING", report["pending"])
    col3.metric("IN PROGRESS", report["in_progress"])
    col4.metric("RESOLVED", report["resolved"])

    st.markdown("""
        <div class="workflow-box">
            <div class="workflow-title">SYSTEM WORKFLOW</div>
            <div style="color: white; font-size: 0.95rem;">Enter Complaint &nbsp;➔&nbsp; Save &nbsp;➔&nbsp; View / Search &nbsp;➔&nbsp; Update Status &nbsp;➔&nbsp; Add Repair Details &nbsp;➔&nbsp; Analyze Data</div>
        </div>
    """, unsafe_allow_html=True)

# ===================== REGISTER =====================
with tabs[1]:
    st.markdown("<h2 style='color: white; font-weight: bold; margin-top: 15px;'>REGISTER A COMPLAINT</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9AA8BA;'>Create a new campus maintenance ticket</p>", unsafe_allow_html=True)
    
    with st.form("complaint_form"):
        st.markdown("<h5 style='color: #F59E0B; font-weight: bold;'>NEW TICKET</h5>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Student Name *")
            building = st.text_input("Building")
            category = st.selectbox("Category", CATEGORIES)
        with col2:
            department = st.text_input("Department")
            room_no = st.text_input("Room No.")
            priority = st.selectbox("Priority", PRIORITIES)
            
        problem = st.text_area("Problem Description *")
        
        submitted = st.form_submit_button("SAVE / REGISTER COMPLAINT")
        if submitted:
            if not student_name.strip() or not problem.strip():
                st.error("Student Name and Problem Description are required.")
            else:
                cid = database.add_complaint(
                    student_name, department, building, room_no, category, problem, priority
                )
                st.success(f"Complaint registered successfully! ID: {cid}")

# ===================== ALL TICKETS =====================
with tabs[2]:
    st.markdown("<h2 style='color: white; font-weight: bold; margin-top: 15px;'>ALL TICKETS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9AA8BA;'>View and manage campus maintenance complaints</p>", unsafe_allow_html=True)
    
    search_id = st.text_input("Search by Complaint ID (e.g., CMP001)")
    if search_id:
        record = database.search_complaint(search_id)
        if record:
            st.json({
                "ID": record[0],
                "Student": record[1],
                "Department": record[2],
                "Building": record[3],
                "Room": record[4],
                "Category": record[5],
                "Problem": record[6],
                "Priority": record[7],
                "Status": record[8],
                "Date": record[9]
            })
        else:
            st.warning("No complaint found with that ID.")

    st.markdown("---")
    
    rows = database.get_all_complaints()
    if rows:
        df = pd.DataFrame(rows, columns=[
            "ID", "Student", "Dept", "Building", "Room", 
            "Category", "Problem", "Priority", "Status", "Date"
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No tickets recorded yet.")

# ===================== MAINTENANCE & STATUS =====================
with tabs[3]:
    st.markdown("<h2 style='color: white; font-weight: bold; margin-top: 15px;'>MAINTENANCE & STATUS</h2>", unsafe_allow_html=True)
    
    sub_tab1, sub_tab2 = st.tabs(["Update Status", "Add Repair Details"])
    
    with sub_tab1:
        st.subheader("Update Complaint Status")
        cid = st.text_input("Complaint ID for Status Update")
        new_status = st.selectbox("New Status", STATUSES)
        
        if st.button("UPDATE STATUS"):
            if cid:
                updated = database.update_status(cid, new_status)
                if updated:
                    st.success(f"Status for {cid.upper()} updated to {new_status}.")
                else:
                    st.error("Complaint ID not found.")
            else:
                st.warning("Please enter a Complaint ID.")
                
    with sub_tab2:
        st.subheader("Add Repair Log")
        with st.form("repair_form"):
            r_cid = st.text_input("Complaint ID")
            staff = st.text_input("Staff Name")
            r_date = st.date_input("Repair Date")
            cost = st.number_input("Repair Cost (₹)", min_value=0.0, step=50.0)
            remarks = st.text_area("Remarks")
            
            if st.form_submit_button("SAVE REPAIR DETAILS"):
                if database.search_complaint(r_cid):
                    database.add_maintenance(r_cid, staff, str(r_date), cost, remarks)
                    st.success(f"Repair details saved for {r_cid.upper()}.")
                else:
                    st.error("Invalid Complaint ID.")

# ===================== REPORTS =====================
with tabs[4]:
    st.markdown("<h2 style='color: white; font-weight: bold; margin-top: 15px;'>REPORTS & ANALYTICS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9AA8BA;'>Pandas analysis and Matplotlib visualizations of maintenance data</p>", unsafe_allow_html=True)
    
    report = analysis.get_report_data()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TOTAL MAINT. COST", f"₹{report['total_cost']:,.2f}")
    c2.metric("AVERAGE REPAIR COST", f"₹{report['average_cost']:,.2f}")
    c3.metric("MOST COMMON CATEGORY", report["common_category"])
    c4.metric("MOST REPORTED BUILDING", report["top_building"])

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Complaints by Category")
        cat_data = analysis.category_data()
        if not cat_data.empty:
            st.bar_chart(cat_data)
        else:
            st.write("No data available.")

    with col_b:
        st.subheader("Complaints by Status")
        status_d = analysis.status_data()
        if not status_d.empty:
            fig, ax = plt.subplots()
            fig.patch.set_facecolor("#101C2D")
            ax.set_facecolor("#101C2D")
            ax.pie(status_d.values, labels=status_d.index, autopct="%1.0f%%", textprops={'color':"w"})
            st.pyplot(fig)
        else:
            st.write("No data available.")