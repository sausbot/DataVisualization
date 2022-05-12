# Import necessary libraries
import pandas as pd
import numpy as np
from bokeh.io import output_file, show, save, curdoc, output_notebook
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, FactorRange, DatetimeTickFormatter
from bokeh.models.widgets import Select
from bokeh.layouts import column, row, gridplot
import bokeh.palettes as bp # uncomment it if you need special colors that are pre-defined
import datetime as dt

#----------------------------Task 1: Data Pre-processing--------------------

# Read data
df = pd.read_csv('data.csv')

# T.1.1: Generate y-axis components.
# Convert "pickup_datetime" and "dropoff_datetime" attributes in the dataframe to datetime type for further processing
df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], yearfirst=True)
df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'], yearfirst=True)

# Adding a new column called "datetime" by extracting the date for the x-axis
df['datetime'] = df['pickup_datetime'].apply(lambda x: x.date())
# Split datetime object to months and hours, and do the following conversion for months:
    # 5 -> "May" 
    # 3 -> "March" , and so on.
# Reference links:
    # https://www.projectpro.io/recipes/split-datetime-data-create-multiple-feature-in-python
df['pickup_datetime_month'] = df['pickup_datetime'].dt.month_name()

# Get the exact time info for starting and ending time for the horizontal bar.
df['pickup_datetime_time'] = df['pickup_datetime'].dt.time
df['dropoff_datetime_time'] = df['dropoff_datetime'].dt.time

# Month conversion
# print(df['pickup_datetime_month'])

# We will remove some part of the data for computational reasons.
np.random.seed(10)
remove_n = 1455000
drop_indices = np.random.choice(df.index, remove_n, replace=False)
df = df.drop(drop_indices)

# Assign colors for each vendor_id. We will need them while plotting.
# Reference Links:
    #https://docs.bokeh.org/en/latest/docs/reference/colors.html

# First create a new column called "color", then assign colors according to vendor_id
    # assign color[0] to vendor_id 1, and color[1] to vendor_id 2
color = list()
for i in range(len(df.index)):
    color.append("#A9A9A9")
df['color'] = color

colors =  ['#FF0000','#32CD32']
for idx in df.index:
    if df.at[idx,'vendor_id'] == 1:
        df.at[idx,'color'] = colors[0]
    else:
        df.at[idx,'color'] = colors[1]

# Replace vendor_id -> 1,2 with "vendor_1","vendor_2"
for idx in df.index:
    df.at[idx,'vendor_id'] = 'vendor_1' if df.at[idx,'vendor_id'] == 1 else 'vendor_2'

# Convert datetime to string using pandas.Timestamp.strftime
df['datetime'] = pd.to_datetime(df['datetime'], yearfirst=True).dt.strftime('%Y-%m-%d')

# T1.2: Create the Selector Widget

# Reference links:
    #https://docs.bokeh.org/en/2.4.0/docs/user_guide/interaction/widgets.html#select
    #https://www.geeksforgeeks.org/bokeh-adding-widgets/

# Add control selector for selecting months, thus you need to first extract the unique month info.
category = df['pickup_datetime_month'].unique().tolist()
select_category = Select(title="Months", value="February", options=category)

print(df)
#-----------------------------------Task2: Construct data structures------------------------------------------

# Group data by month
grouped_months = df.groupby('pickup_datetime_month')

# T2.1 : Define a function that creates a ColumnDataSource
    #INPUT: month
    #OUTPUT: ColumnDataSource
def create_datasource(month):
    month_df = grouped_months.get_group(month).drop(['pickup_longitude', "pickup_latitude","dropoff_longitude","dropoff_latitude","store_and_fwd_flag"],1)
    
    data = {'Vendor': list(month_df['vendor_id']),
            'NumOfPass': list(month_df['passenger_count']),
            'StartTime': list(month_df['pickup_datetime_time']),
            'EndTime': list(month_df['dropoff_datetime_time']),
            'Dates' : month_df.loc[:,"datetime"].sort_values(),
            'Color' : list(month_df['color'])
    }

    source = ColumnDataSource(data=data)
    
    return source

# T2.2: Define a function that updates the datasource when another month is selected.
def update_source(attr, old, new):
    month = select_category.value # once the widget is trigered, a new value will be passed.
    source1 = create_datasource(month) # with the new month value, we update the ColumnDataSource, such that the plot will be updated.
    p.y_range.factors = list(source1.data['Dates'].unique()) # We also need to update the y axis since the date in each month is unique.
    source.data.update(source1.data) # This adds a new dict. We will replace the whole datasource
    

# Bind the update_source function to select_category widget. Everytime a new item is selected the update_source
# function will be triggered
select_category.on_change("value", update_source)

#------------------------------------Task3: Plotting---------------------------------------------------------

# Your y-range should be the dates for the selected month.
# Hint: Keep in mind that as the month changes your y-range also needs to be updated. 

# T3.1: Get the current month, create the data source based on the new month info, and define the y-range
current_month = select_category.value
source = create_datasource(current_month)
y_Range = list(dict.fromkeys(source.data['Dates']))

# T3.2: Create figure and add the necessary glyphs: Horizontal Bar (HBar) and cirle.
p = figure(x_axis_type="datetime", y_range = y_Range, plot_width=1400, plot_height=700, toolbar_location=None,title="NYC Taxi Traffic")
p.xaxis.formatter = DatetimeTickFormatter(hours=["%H:%M"], days=["%H:%M"], months=["%H:%M"], years=["%H:%M"],)

# Color of the bars and circles changes depending on the vendor_id. Structure your code accordingly ;)
p.hbar(y="Dates", right="StartTime", left="EndTime", height=0.05, source=source, line_color="Color")
circle = p.circle(y="Dates", x="StartTime", size='NumOfPass', source=source, alpha=0.8, color="Color")

# T3.3: Add Hover Tool to circle glyph. It must show the date, number of passengers and vendor_id.
p.add_tools(HoverTool(renderers=[circle], tooltips=[
    	("Date","@Dates"),
        ("Number of Passengers", "@NumOfPass"),
        ("Vendor ID", "@Vendor"),
    ],
	formatters={
		'@Dates' : 'datetime',
	}
	))

# Add labels and create the layout
p.yaxis.axis_label = "Dates"
p.xaxis.axis_label = "Time"
p.sizing_mode = "stretch_both"

layout = column(p, select_category)
curdoc().add_root(layout)

# Save the plot as "dvc_ex2.html" using output_file
output_file(filename="dvc_ex2.html", title="NYC Taxi Traffic")
save(p)

# You can use the command below in the folder of your python file to start a bokeh directory app.
# bokeh serve --show ex2.py or bokeh serve --show ex2.ipynb
# python -m bokeh serve --show ex2.py