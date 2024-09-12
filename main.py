import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set the title and favicon for the dashboard
st.set_page_config(
    page_title='Church Attendance Dashboard',
    page_icon=':church:',
)

# Define a color palette to use for all plots
color_palette = {
    'Members': '#17a589',     # Teal
    'Guests': '#f4a261',  # Muted Rose
    'First Timers': '#4682b4', # Steel Blue
    '2nd/3rd Timers': '#dc143c',     # Crimson
    'Children': '#a27ea8',     # Muted Lavender
    'Retained': '#17a589',     # Teal
    'Not Retained': '#f4a261'  # Muted Rose
}

# Load credentials from Streamlit secrets
credentials_dict = {
    "type": st.secrets["gcp_service_account"]["type"],
    "project_id": st.secrets["gcp_service_account"]["project_id"],
    "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
    "private_key": st.secrets["gcp_service_account"]["private_key"],
    "client_email": st.secrets["gcp_service_account"]["client_email"],
    "client_id": st.secrets["gcp_service_account"]["client_id"],
    "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
    "token_uri": st.secrets["gcp_service_account"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"]
}

# -----------------------------------------------------------------------------
# Function to load the dataset
@st.cache_data
# -----------------------------------------------------------------------------
# Function to load attendance data from Google Sheets
def load_attendance_data_from_google_sheet():
    # Define the scope of access
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Add your service account JSON file path
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_dict, scope)

    # Authorize and create a connection to the sheet
    client = gspread.authorize(creds)

    # Open the Google Sheet by its name or URL
    sheet = client.open('Attendance').sheet1

    # Get all the data from the Google Sheet
    data = sheet.get_all_records()

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data)

    # Convert 'Date' column to datetime if necessary
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')

    return df

# -----------------------------------------------------------------------------
# Use the Google Sheet data
attendance_df = load_attendance_data_from_google_sheet()

# -----------------------------------------------------------------------------
# Draw the dashboard

st.title('TheNew Island Dashboard')

# -----------------------------------------------------------------------------
# Function to filter data based on time range selection
def filter_by_time_range(df, time_range):
    end_date = df['Date'].max()  # Most recent Sunday
    if time_range == 'Last 3 months':
        start_date = end_date - pd.DateOffset(months=3)
    elif time_range == 'Last 6 months':
        start_date = end_date - pd.DateOffset(months=6)
#    elif time_range == 'Last 1 year':
#        start_date = end_date - pd.DateOffset(years=1)
    elif time_range == 'First quarter':
        start_date = pd.Timestamp(f'{end_date.year}-01-01')
        end_date = pd.Timestamp(f'{end_date.year}-03-31')
    elif time_range == 'Second quarter':
        start_date = pd.Timestamp(f'{end_date.year}-04-01')
        end_date = pd.Timestamp(f'{end_date.year}-06-30')
    elif time_range == 'Third quarter':
        start_date = pd.Timestamp(f'{end_date.year}-07-01')
        end_date = pd.Timestamp(f'{end_date.year}-09-30')
#    elif time_range == 'Fourth quarter':
#        start_date = pd.Timestamp(f'{end_date.year}-10-01')
#        end_date = pd.Timestamp(f'{end_date.year}-12-31')
    else:
        start_date = df['Date'].min()

    return df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

# -----------------------------------------------------------------------------
# Time range selection
time_range = st.selectbox(
    'Select the time range to view:',
    ['Last 3 months', 'Last 6 months', 'First quarter', 'Second quarter','Third quarter', 'All time'],
    index=0  # Default to 'Last 3 months'
)

# Filter data based on the selected time range
filtered_attendance_df = filter_by_time_range(attendance_df, time_range)

# Visualize key metrics
st.header('Attendance Metrics')

total_members = filtered_attendance_df['Members'].sum()
total_guests = filtered_attendance_df['Guests'].sum()
total_first_timers = filtered_attendance_df['First Timers'].sum()
total_second_third_timers = filtered_attendance_df['2nd/3rd Timers'].sum()
total_children = filtered_attendance_df['Children'].sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric('Total Members', 224)
with col2:
    st.metric('Total First Timers', total_first_timers)
with col3:
    st.metric('Total 2nd/3rd Timers', total_second_third_timers)
with col4:
    st.metric('Total Children', 8)
#with col5:
#    st.metric('Total Guests', total_guests)


# -----------------------------------------------------------------------------
# Visualize the trends and the pie chart side by side

col1, col2 = st.columns([2, 1])

# Column 1: Line plot for attendance trends
with col1:
    # Plot for attendance trends over time
    fig, ax = plt.subplots()

    # Plot Members
    ax.plot(filtered_attendance_df['Date'], filtered_attendance_df['Members'],
            marker='.', color=color_palette['Members'], label='Members', linestyle='-', linewidth=1)

    # Plot Guests
    ax.plot(filtered_attendance_df['Date'], filtered_attendance_df['Guests'],
            marker='.', color=color_palette['Guests'], label='Guests', linestyle='-', linewidth=1)

    # Plot First Timers
    ax.plot(filtered_attendance_df['Date'], filtered_attendance_df['First Timers'],
            marker='.', color=color_palette['First Timers'], label='First Timers', linestyle='-', linewidth=1)

    # Customize the plot
    ax.set_title('Attendance Trends Over Time', color='white')
    ax.set_xlabel('Date', color='white')
    ax.set_ylabel('Count', color='white')

    # Rotate x-axis labels and set tick color
    ax.tick_params(axis='x', rotation=45, colors='white')
    ax.tick_params(axis='y', colors='white')

    # Grid lines and transparency
    ax.yaxis.grid(True)
    ax.xaxis.grid(False)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # Display the line plot
    st.pyplot(fig)

# Column 2: Pie chart for retention rate
with col2:
    # Retention rate calculation (First Timers who become 2nd/3rd Timers)
    total_first_timers = filtered_attendance_df['First Timers'].sum()
    total_retained = filtered_attendance_df['2nd/3rd Timers'].sum()

    if total_first_timers > 0:
        retention_rate = (total_retained / total_first_timers) * 100
    else:
        retention_rate = 0

    # Create a pie chart for retention rate with transparent background
    # Pie chart for retention rate
    labels = ['Retained', 'Not Retained']
    sizes = [total_retained, total_first_timers - total_retained]
    colors = [color_palette['Retained'], color_palette['Not Retained']]

    fig, ax = plt.subplots(figsize=(5, 5), facecolor='none')
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle

    # Transparent background
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # Add a legend
    ax.legend(wedges, labels, title="Status", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    st.text('First Timers Retention Rate')
    st.pyplot(fig)

# -----------------------------------------------------------------------------
# Display the filtered data as a table without the time and index
st.subheader('Attendance Data')

# -----------------------------------------------------------------------------
# Checkbox to filter special services
show_special_events_only = st.checkbox('Show only special services')

# -----------------------------------------------------------------------------
# Function to filter data based on special events
def filter_by_special_event(df, show_special_events_only):
    if show_special_events_only:
        # Filter to show only rows where there is a special event
        return df[df['Special Sunday Service'] != 'No']
    return df

# Filter data based on the checkbox state
filtered_attendance_df = filter_by_special_event(attendance_df, show_special_events_only)

# -----------------------------------------------------------------------------
# Format the 'Date' column to remove the time display
filtered_attendance_df = filtered_attendance_df.copy()
filtered_attendance_df['Date'] = filtered_attendance_df['Date'].dt.strftime('%d/%m/%Y')

# Display the filtered data in a table
st.dataframe(filtered_attendance_df)

# -----------------------------------------------------------------------------
# Visualize special event attendance if applicable
if show_special_events_only and not filtered_attendance_df.empty:
    st.subheader('Special Sunday Service')

    # Plot bar chart for attendance during special events
    fig, ax = plt.subplots(figsize=(4, 2))

    filtered_attendance_df.plot(
        x='Special Sunday Service',
        y=['Members', 'Guests', 'First Timers', '2nd/3rd Timers', 'Children'],
        kind='barh',
        stacked=True,
        ax=ax,
        color=[color_palette['Members'], color_palette['Guests'], color_palette['First Timers'],
               color_palette['2nd/3rd Timers'], color_palette['Children']]

    )

    # Customize the plot
    #ax.set_title('Attendance for Special Events', color='white', fontsize=5)
    ax.set_xlabel('Count', color='white', fontsize=6)
    ax.set_ylabel('Special Event', color='white', fontsize=6)

    # Rotate y-axis labels
    ax.set_yticklabels(ax.get_yticklabels(), rotation=45, ha='right', color='white', fontsize=6)

    ax.tick_params(axis='y', colors='white', labelsize=6)
    ax.tick_params(axis='x', colors='white', labelsize=6)

    # Customize the legend
    ax.legend(fontsize=4)

    # Transparent background
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # Show the plot
    st.pyplot(fig)
elif show_special_events_only and filtered_attendance_df.empty:
    st.write('No special events found.')


# -----------------------------------------------------------------------------
# Feature to compare Quarters
st.subheader('Compare Metrics For Different Quarters')

# Function to filter data by quarter
def filter_by_quarter(df, quarter):
    year = df['Date'].max().year  # Get the current year
    if quarter == 'First quarter':
        start_date, end_date = f'{year}-01-01', f'{year}-03-31'
    elif quarter == 'Second quarter':
        start_date, end_date = f'{year}-04-01', f'{year}-06-30'
    elif quarter == 'Third quarter':
        start_date, end_date = f'{year}-07-01', f'{year}-09-30'
    elif quarter == 'Fourth quarter':
        start_date, end_date = f'{year}-10-01', f'{year}-12-31'
    return df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

# Multi-select for quarters
quarter_options = ['First quarter', 'Second quarter', 'Third quarter', 'Fourth quarter']
selected_quarters = st.multiselect('Select quarters to compare:', quarter_options)

# Add a button to trigger the comparison after selecting quarters
if st.button('Compare Selected Quarters'):
    if len(selected_quarters) < 2:
        st.warning("Please select at least two quarters to compare.")
    else:
        # Filter data for each selected quarter
        filtered_data_quarters = {quarter: filter_by_quarter(attendance_df, quarter) for quarter in selected_quarters}

        # Calculate key metrics for each quarter
        def calculate_metrics(df):
            return {
                'Total First Timers': df['First Timers'].sum(),
                'Total 2nd/3rd Timers': df['2nd/3rd Timers'].sum()
            }

        metrics = {quarter: calculate_metrics(filtered_data) for quarter, filtered_data in filtered_data_quarters.items()}

        # Create columns to display metrics side by side for all selected quarters
        cols = st.columns(len(selected_quarters))

        for i, quarter in enumerate(selected_quarters):
            with cols[i]:
                st.markdown(f"**{quarter} Metrics**")
                for key, value in metrics[quarter].items():
                    st.metric(label=key, value=value)

        # Visualize the comparison using a bar chart
        fig, ax = plt.subplots(figsize=(4, 2))

        categories = ['First Timers', '2nd/3rd Timers']

        # Adjust color mapping to differentiate quarters
        quarter_colors = ['#17a589','#f4a261']

        # Plot each quarter with its own color
        for i, quarter in enumerate(selected_quarters):
            values = [metrics[quarter][f'Total {category}'] for category in categories]
            ax.bar([x + i * 0.2 for x in range(len(categories))], values, width=0.2, label=quarter,
                   color=quarter_colors[i])

        # Add labels and formatting
        ax.set_xlabel('Metrics', fontsize=8, color='white')
        ax.set_ylabel('Count', fontsize=8, color='white')
        ax.set_title('Attendance Metrics for Selected Quarters', fontsize=10, color='white')

        # X-axis categories
        ax.set_xticks([x + 0.2 for x in range(len(categories))])
        ax.set_xticklabels(categories, color='white')

        # Y-axis tick color
        ax.tick_params(axis='y', colors='white')

        # Add legend
        ax.legend(fontsize=5)

        # Transparent background
        fig.patch.set_alpha(0)
        ax.set_facecolor('none')

        st.pyplot(fig)


# -----------------------------------------------------------------------------
# Function to filter data based on special service inclusion/exclusion
def filter_attendance_by_service(df, include_special_service):
    if include_special_service:
        return df[df['Special Sunday Service'] != 'No']
    else:
        return df[df['Special Sunday Service'] == 'No']


# -----------------------------------------------------------------------------
# Function to get highest and lowest attendance
def get_attendance_extremes(df, highest=True):
    if highest:
        max_row = df[df['Total Check-in'] == df['Total Check-in'].max()].copy()
        max_row['Date'] = max_row['Date'].dt.date  # Remove time from Date
        return max_row
    else:
        min_row = df[df['Total Check-in'] == df['Total Check-in'].min()].copy()
        min_row['Date'] = min_row['Date'].dt.date  # Remove time from Date
        return min_row

# -----------------------------------------------------------------------------
# Section for highest/lowest attendance with/without special service
st.subheader('View High/Low Attendance')

# User selects an option to view specific attendance extremes
attendance_extreme_option = st.selectbox(
    'Select an option to view attendance extremes:',
    options=[
        'Select an option',
        'View peak attendance with special Sunday service',
        'View peak attendance without special Sunday service',
        'View low attendance with special Sunday service',
        'View low attendance without special Sunday service'
    ],
    index=0
)

# Dictionary to map user options to conditions
attendance_conditions = {
    'View peak attendance with special Sunday service': {'highest': True, 'special_service': True},
    'View peak attendance without special Sunday service': {'highest': True, 'special_service': False},
    'View low attendance with special Sunday service': {'highest': False, 'special_service': True},
    'View low attendance without special Sunday service': {'highest': False, 'special_service': False}
}

# Process the user's selection
if attendance_extreme_option != 'Select an option':
    # Get the corresponding condition based on user's selection
    conditions = attendance_conditions[attendance_extreme_option]

    # Filter attendance data based on whether to include special services
    filtered_data = filter_attendance_by_service(attendance_df, conditions['special_service'])

    # Get the highest or lowest attendance based on the user's selection
    attendance_extreme = get_attendance_extremes(filtered_data, highest=conditions['highest'])

    # Display the attendance data
    if not attendance_extreme.empty:
        st.write(f"{'Peak' if conditions['highest'] else 'Low'} attendance with{'out' if not conditions['special_service'] else ''} special Sunday service:")
        st.dataframe(attendance_extreme)
    else:
        st.write('No attendance data found for the selected criteria.')
else:
    st.write('Please select an option to view attendance extremes.')
