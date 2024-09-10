import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Set the title and favicon for the dashboard
st.set_page_config(
    page_title='Church Attendance Dashboard',
    page_icon=':church:',
)

# -----------------------------------------------------------------------------
# Function to load the dataset
@st.cache_data
def get_attendance_data():
    df = pd.read_csv('data/Attendance-Metrics.csv')

    # Convert 'Date' column to datetime format
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

    # Replace NaNs with zeros
    df.fillna(0, inplace=True)
    return df

attendance_df = get_attendance_data()

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
    fig, ax = plt.subplots()

    # Plot Members
    ax.plot(filtered_attendance_df['Date'], filtered_attendance_df['Members'],
            marker='.', color='blue', label='Members', linestyle='-', linewidth=1)

    # Plot Guests
    ax.plot(filtered_attendance_df['Date'], filtered_attendance_df['Guests'],
            marker='.', color='red', label='Guests', linestyle='-', linewidth=1)

    # Plot First Timers
    ax.plot(filtered_attendance_df['Date'], filtered_attendance_df['First Timers'],
            marker='.', color='yellow', label='First Timers', linestyle='-', linewidth=1)

    # Customize the plot
    ax.set_title('Attendance Trends Over Time', color='white')

    # Set x and y labels to white
    ax.set_xlabel('Date', color='white')
    ax.set_ylabel('Count', color='white')

    # Customize the legend
    ax.legend()

    # Rotate date labels for better readability
    plt.xticks(rotation=45, color='white')

    # Set y-ticks color
    ax.tick_params(axis='y', colors='white')

    # Set x-ticks color
    ax.tick_params(axis='x', colors='white')

    # Show only horizontal grid lines
    ax.yaxis.grid(True)  # Horizontal grid
    ax.xaxis.grid(False)  # No vertical grid

    # Set background to transparent
    fig.patch.set_alpha(0)  # Figure background
    ax.set_facecolor('none')  # Axes background

    # Display the plot in Streamlit
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
    labels = ['Retained', 'Not Retained']
    sizes = [total_retained, total_first_timers - total_retained]
    colors = ['#66b3ff', '#ff6666']

    # Set the figure size to make the pie chart smaller
    fig, ax = plt.subplots(figsize=(5, 5), facecolor='none')  # Set facecolor to 'none' for transparency
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    # Add a legend to the pie chart
    ax.legend(wedges, labels, title="Status", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    st.text('First Timers Retention Rate')
    st.pyplot(fig)

# Display the filtered data as a table without the time and index
st.header('Attendance Data')

# Format the 'Date' column to remove the time and show only the date
filtered_attendance_df['Date'] = filtered_attendance_df['Date'].dt.strftime('%d/%m/%Y')

# Reset the index to avoid displaying the original DataFrame index
filtered_attendance_df = filtered_attendance_df.reset_index(drop=True)
st.dataframe(filtered_attendance_df)
