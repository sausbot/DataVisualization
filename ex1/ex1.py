#!/usr/bin/env python
# coding: utf-8


# Import necessary libraries
import pandas as pd
from bokeh.io import output_file, show, save
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, FactorRange
import bokeh.palettes as bp

# Task 1: Data Pre-processing
# Read data into a dataframe using pandas
df = pd.read_csv('data.csv')

# Convert "pickup_datetime" attribute in the dataframe to datetime type for further processing
df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], yearfirst=True)

# Split datetime object to months and hours, and change month to month name
df['pickup_datetime_month'] = df['pickup_datetime'].dt.month_name()
df['pickup_datetime_hour'] = df['pickup_datetime'].dt.hour

# Use months as stack names
stacks = ["January", "February", "March", "April", "May", "June"]

# Calculate the total number of trips for each month grouped by hour
month_stack_values = [ df.groupby(['pickup_datetime_month']).get_group(month).groupby(['pickup_datetime_hour']).size() for month in stacks ]

# Create dict with month name as key and stack values as members
data = dict(zip(stacks, month_stack_values))

# Manipulate "pickup_datetime_hour" attribute for visualization purposes.
# Extract unique values for pickup_datetime_hour and create the time intervals(0 -> 0-1 , 23 -> 23-0 and so on) using string manipulation.
hours = df['pickup_datetime_hour'].unique().tolist()
hours.sort()
hours_str = [ f"{hour}-{hour+1}" if hour < 23 else f"{hour}-0" for hour in hours ]
data["Hours"] = hours_str

# Task 2: Data Visualization
# Using the information gathered from the data pre-processing step create the ColumnDataSource for visualization.
source = ColumnDataSource(data)

# Visualize the data using bokeh plot functions
p=figure(x_range=FactorRange(*hours_str), plot_height=800, plot_width=800, title='Number of trips in NYC')
p.yaxis.axis_label = "Number of Trips"
p.xaxis.axis_label = "Hours"
p.sizing_mode = "stretch_both"
p.xgrid.grid_line_color = None

# Choose colours for graph
colors = bp.Viridis[6]

# Using vbar_stack to plot the stacked bar chart
p.vbar_stack(stacks, x='Hours', source=source, fill_color=colors, legend_label=stacks, width=0.8)

# Add HoverTool. HoverTool should show the name of the month, the hours and the number of trips when the mouse hover on each bar.
hover = HoverTool(tooltips = [
    ('Month', '$name'),
    ('Hour', '@Hours'),
    ('Number of Trips', '@$name'),           
    ])
p.add_tools(hover)
show(p)

# Save the plot as "dvc_ex1.html" using output_file
output_file(filename="dvc_ex1.html", title="Number of Trips Grouped by Month")
save(p)
