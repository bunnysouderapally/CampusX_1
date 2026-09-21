import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import database
import analysis

# Page configuration
st.set_page_config(page_title="CampusFix", page_icon="🛠️", layout="wide")

# Ensure database tables exist
database.create_database()

# Sidebar Navigation
st.sidebar.title("CampusFix Menu")
page = st.sidebar.radio(
    "Navigate", 
    ["Dashboard", "Register Complaint", "All Tickets", "Maintenance & Status", "Reports"]
)

CATEGORIES = ["Electrical", "Furniture", "Plumbing", "IT", "Internet", "Cleaning", "AC/Cooling", "Other"]
PRIORITIES = ["Low", "Medium", "High"]
STATUSES = ["Pending", "In Progress", "Resolved"]

# ===================== DASHBOARD =====================
if page == "Dashboard":
    st.title("🛠️ Campus Maintenance System")
    st.subheader("Complaint & Tracking Dashboard")
    
    report = analysis.get_report_data()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Complaints", report["total"])
    col2.metric("Pending", report["pending"])
    col3.metric("In Progress", report["in_progress"])
    col4.metric("Resolved", report["resolved"])

    st.markdown("---")
    st.info("**Workflow:** Enter Complaint ➔ Save ➔ View/Search ➔ Update Status ➔ Add Repair Details ➔ Analyze Data")

# ===================== REGISTER COMPLAINT =====================
elif page == "Register Complaint":
    st.title("📝 Register a Complaint")
    
    with st.form("complaint_form"):
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
        
        submitted = st.form_submit_button("Submit Complaint")
        if submitted:
            if not student_name.strip() or not problem.strip():
                st.error("Student Name and Problem Description are required.")
            else:
                cid = database.add_complaint(
                    student_name, department, building, room_no, category, problem, priority
                )
                st.success(f"Complaint registered successfully! ID: **{cid}**")

# ===================== ALL TICKETS =====================
elif page == "All Tickets":
    st.title("📋 All Maintenance Tickets")
    
    search_id = st.text_input("Search by Complaint ID (e.g., CMP001)")
    if search_id:
        record = database.search_complaint(search_id)
        if record:
            st.json({
                "Complaint ID": record[0],
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
elif page == "Maintenance & Status":
    st.title("⚙️ Ticket Management")
    
    tab1, tab2 = st.tabs(["Update Status", "Add Repair Details"])
    
    with tab1:
        st.subheader("Update Complaint Status")
        cid = st.text_input("Complaint ID for Status Update")
        new_status = st.selectbox("New Status", STATUSES)
        
        if st.button("Update Status"):
            if cid:
                updated = database.update_status(cid, new_status)
                if updated:
                    st.success(f"Status for {cid.upper()} updated to {new_status}.")
                else:
                    st.error("Complaint ID not found.")
            else:
                st.warning("Please enter a Complaint ID.")
                
    with tab2:
        st.subheader("Add Repair Log")
        with st.form("repair_form"):
            r_cid = st.text_input("Complaint ID")
            staff = st.text_input("Staff Name")
            r_date = st.date_input("Repair Date")
            cost = st.number_input("Repair Cost (₹)", min_value=0.0, step=50.0)
            remarks = st.text_area("Remarks")
            
            if st.form_submit_button("Save Repair Details"):
                if database.search_complaint(r_cid):
                    database.add_maintenance(r_cid, staff, str(r_date), cost, remarks)
                    st.success(f"Repair details saved for {r_cid.upper()}.")
                else:
                    st.error("Invalid Complaint ID.")

# ===================== REPORTS =====================
elif page == "Reports":
    st.title("📊 Reports & Analytics")
    
    report = analysis.get_report_data()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Maintenance Cost", f"₹{report['total_cost']:,.2f}")
    col2.metric("Average Repair Cost", f"₹{report['average_cost']:,.2f}")
    col3.metric("Most Common Category", report["common_category"])
    col4.metric("Top Reported Building", report["top_building"])

    st.markdown("---")
    
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
            ax.pie(status_d.values, labels=status_d.index, autopct="%1.0f%%")
            st.pyplot(fig)
        else:
            st.write("No data available.")