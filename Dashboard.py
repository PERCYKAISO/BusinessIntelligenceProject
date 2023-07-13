
import dash
from dash.dependencies import Input, Output
from dash.dash_table.Format import Group
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import dash_table
import pyodbc

# Database connection
conn = pyodbc.connect("Driver={SQL Server};"
    "Server=L421\SQLEXPRESS;"
    "Database=DWAdventureWorks;"
    "Trusted_Connection=yes;"
                    )

# Queries section starts here
qs_1 = pd.read_sql_query('''SELECT GroupName, COUNT(*) GroupN,
CASE
WHEN GroupName = 'PACIFIC' THEN 'PACIFIC'
WHEN GroupName = 'NORTH AMERICA' THEN 'NORTH AMERICA'
WHEN GroupName = 'EUROPE' THEN 'EUROPE'
END 'Grp'
FROM DWAdventureWorks.Sales.DimSalesPerson
GROUP BY GroupName''', conn)

# Calculate percentages
qs_1['Percentage'] = qs_1['GroupN'] / qs_1['GroupN'].sum() * 100

# Create the pie chart using Plotly Express
fig_pie = px.pie(qs_1, values='GroupN', names='Grp', hole=.3, labels={'Grp': 'Sales Region'},title='Number of Sales by Region')

# Add percentages to the chart
labels = [f"{row['Grp']}: {row['Percentage']:.1f}%" for index, row in qs_1.iterrows()]
fig_pie.update_traces(textposition='inside', textinfo='label+percent', text=labels)

df_line = pd.read_sql_query('''
SELECT Year, COUNT(*) Order_Rates FROM(

SELECT YEAR(RateChangeDate) Year,

CASE
    WHEN MONTH(RateChangeDate) IN (1,2,3) THEN 'Q1'
    WHEN MONTH(RateChangeDate) IN (4,5,6) THEN 'Q2'
    WHEN MONTH(RateChangeDate) IN (7,8,9) THEN 'Q3'
    WHEN MONTH(RateChangeDate) IN (10,11,12) THEN 'Q4'
END 'Qrt',
MONTH (RateChangeDate) MM,
DAY(RateChangeDate) DD

FROM DWAdventureWorks.HumanResources.DimDepartment

)tmp
GROUP BY Year''', conn)

fig_line = px.line(df_line, x='Year', y='Order_Rates',title='Order Rates By Year')

prod_query = '''
SELECT Color, COUNT(*) AS Number_Of_Product, STRING_AGG(Name, ', ') AS ProductNames
FROM [DWAdventureWorks].[Production].[ProductInformationDimension]
GROUP BY Color
ORDER BY Number_Of_Product DESC;'''

diff = pd.read_sql_query(prod_query, conn)

# Create a color map
color_map = {
    'Black': 'black',
    'Blue': 'blue',
    'Grey': 'grey',
    'Multi': 'orange',
    'Red': 'red',
    'Silver': 'silver',
    'Silver/B': 'silver',
    'Unknown': 'grey',
    'White': 'white',
    'Yellow': 'yellow'
}

diff['ColorCode'] = diff['Color'].apply(lambda x: color_map.get(x, 'green'))

# Plot the data using the color codes
fig_prod = px.bar(diff, x='Color', y='Number_Of_Product', color='ColorCode', title='Number of Products by Color')



df3_line = pd.read_sql_query('''
    SELECT 
        DATEPART(YEAR, OrderDate) AS Year,
        DATEPART(MONTH, OrderDate) AS Month,
        SUM(TotalDue) AS SalesTotal
    FROM 
        [DWAdventureWorks].[Sales].[FactSales]
    GROUP BY 
        DATEPART(YEAR, OrderDate),
        DATEPART(MONTH, OrderDate)
    ORDER BY 
        Year, Month''', conn)

fig_line2 = px.line(df3_line, x='Month', y='SalesTotal', color='Year',
                   title='Total Sales by Month and Year')

df = pd.read_sql_query('''
    SELECT ShipMethodID, Name
    FROM [DWAdventureWorks].[Purchasing].[DimShipMethod]
''', conn)

# Create the bar graph
fig_bar = px.bar(df, x='Name', y='ShipMethodID', labels={
    'Name': 'Shipping Method',
    'ShipMethodID': 'Number of Shipments'
}, title='Number of Shipments by Shipping Method')

####

query = "SELECT YEAR(LastReceiptDate) AS Year, COUNT(*) AS ProductCount FROM [DWAdventureWorks].[Purchasing].[DimProduct] GROUP BY YEAR(LastReceiptDate) ORDER BY YEAR(LastReceiptDate)"
df = pd.read_sql(query, conn)

# Create bar graph using Plotly Express
fig2 = px.bar(df, x='Year', y='ProductCount', title='Product Sales by Year')

# ) ##
# 

query = ''' SELECT YEAR(OrderDate) AS Year, COUNT(SalesOrderDetailID) AS Count
FROM [DWAdventureWorks].[Sales].[FactSales]
GROUP BY YEAR(OrderDate)'''

# Reading data into pandas dataframe
df = pd.read_sql(query, conn)

# Create a bar graph
fig3 = go.Figure(
    data=[go.Bar(x=df['Year'], y=df['Count'])],
    layout=go.Layout(
        title=go.layout.Title(text='Sales Order Details by Year'),
        xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text='Year')),
        yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text='Sales Order Count')),
        plot_bgcolor="#F2F2F2"
    )
)
# 
# ##



query = '''
    SELECT 
        ToCurrencyCode,
        COUNT(*) AS TotalCount
    FROM 
        [DWAdventureWorks].[Sales].[DimCurrency]
    GROUP BY 
        ToCurrencyCode
'''

# Execute the query and load the results into a pandas DataFrame
df = pd.read_sql_query(query, conn)

# Calculate the percentage of each currency in the total
df['Percentage'] = df['TotalCount'] / df['TotalCount'].sum() * 100

# Create the pie chart using plotly
fig = px.pie(df, values='Percentage', names='ToCurrencyCode', title='Percentage of Currency Transactions')

app = dash.Dash(__name__)


# Define the navigation bar
app.title = 'GROUP - DASHBOARD'
nav_bar = html.Div(
    style={  'padding': '20px', 'fontsize': '20px'},

    children=[
        html.H1('GROUP2 - DASHBOARD',style={'color': 'white','text-align': 'center', }),
    ]
)


graph_section = html.Div(
    style={'display': 'flex','flex-direction': 'row','flex-wrap': 'wrap','overflow': 'hidden'},
    children = [
        dcc.Graph(id="barmode", figure=fig_pie, style={'width': '50%'}),
        dcc.Graph(id="bar", figure=fig_line, style={'width': '50%'}),
        dcc.Graph(id="barmod", figure=fig_prod, style={'width': '50%'}),
        dcc.Graph(id="ba", figure=fig_line2, style={'width': '50%'}),
        dcc.Graph(id="ba", figure=fig_bar, style={'width': '50%'}),
        dcc.Graph(id="ba", figure=fig, style={'width': '50%'}),
        dcc.Graph(id="ba", figure=fig2, style={'width': '50%'}),
        dcc.Graph(id="ba", figure=fig3, style={'width': '50%'}),
        

    ]
)


app.layout = html.Div(
    style={'background-color': '#330000'},
    children=[
        nav_bar,
        
        graph_section,
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)
