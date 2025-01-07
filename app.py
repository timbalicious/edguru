import streamlit as st
import requests
from datetime import datetime
import pytz

# Title of the app
st.title('ED Guru')

# Header
st.header('Welcome to my app')

# Fetch the list of commodities from the API
response = requests.get('https://api.ardent-industry.com/v1/commodities')
commodities = response.json()

# Extract commodity names where totalStock and totalDemand are not null
commodity_names = [commodity['commodityName'] for commodity in commodities 
                   if commodity['totalStock'] is not None and commodity['totalDemand'] is not None]

# Select box for commodities
commodity = st.selectbox('Select a commodity:', commodity_names)

# Fetch and display the selected commodity details
with st.expander('Summary'):
    if commodity:
        commodity_response = requests.get(f'https://api.ardent-industry.com/v1/commodity/name/{commodity}')
        commodity_details = commodity_response.json()
        
        # Function to convert timestamp to "X days, Y hours, Z minutes ago"
        def time_ago(timestamp):
            time_diff = datetime.now(pytz.utc) - datetime.fromisoformat(timestamp).astimezone(pytz.utc)
            days_ago = time_diff.days
            hours_ago, remainder = divmod(time_diff.seconds, 3600)
            minutes_ago = remainder // 60
            return f"{days_ago} days, {hours_ago} hours, {minutes_ago} minutes ago"

        # Modify the commodity details to include "X days, Y hours, Z minutes ago" for the timestamp
        if 'timestamp' in commodity_details:
            commodity_details['timestamp'] = time_ago(commodity_details['timestamp'])

        # Display the commodity details in a table
        st.table(commodity_details)

# Section for Exporters
with st.expander('Exporters'):
    # Query parameters
    min_volume = st.number_input('Minimum Volume', min_value=1, value=1)
    max_price = st.number_input('Maximum Price', min_value=1, value=1)
    station_type_option = st.selectbox('Station Type', options=['Stations and Carriers', 'Carriers Only', 'Stations Only'])
    max_days_ago = st.number_input('Maximum Days Ago', min_value=1, value=30)

    if commodity:
        params = {
            'minVolume': min_volume,
            'maxPrice': max_price,
            'fleetCarriers': None if station_type_option == 'Stations and Carriers' else (1 if station_type_option == 'Carriers Only' else 0),
            'maxDaysAgo': max_days_ago
        }

        # Remove None values from params
        params = {k: v for k, v in params.items() if v is not None}

        exporters_response = requests.get(f'https://api.ardent-industry.com/v1/commodity/name/{commodity}/exports', params=params)
        exporters = exporters_response.json()

        # Filter the exporter data to display only the specified fields
        filtered_exporters = [
            {
                'stationName': exporter['stationName'],
                'stationType': exporter['stationType'],
                'distanceToArrival': exporter['distanceToArrival'],
                'maxLandingPadSize': exporter['maxLandingPadSize'],
                'systemName': exporter['systemName'],
                'buyPrice': exporter['buyPrice'],
                'stock': exporter['stock'],
                'updatedAt': time_ago(exporter['updatedAt']) if 'updatedAt' in exporter else None
            }
            for exporter in exporters
        ]
        
        # Display the filtered exporters data in a table
        st.table(filtered_exporters)

# Section for Importers
with st.expander('Importers'):
    # Query parameters
    min_volume = st.number_input('Minimum Volume', min_value=1, value=1, key='import_min_volume')
    min_price = st.number_input('Minimum Price', min_value=1, value=1, key='import_min_price')
    station_type_option = st.selectbox('Station Type', options=['Stations and Carriers', 'Carriers Only', 'Stations Only'], key='import_station_type')
    max_days_ago = st.number_input('Maximum Days Ago', min_value=1, value=30, key='import_max_days_ago')

    if commodity:
        params = {
            'minVolume': min_volume,
            'minPrice': min_price,
            'fleetCarriers': None if station_type_option == 'Stations and Carriers' else (1 if station_type_option == 'Carriers Only' else 0),
            'maxDaysAgo': max_days_ago
        }

        # Remove None values from params
        params = {k: v for k, v in params.items() if v is not None}

        importers_response = requests.get(f'https://api.ardent-industry.com/v1/commodity/name/{commodity}/imports', params=params)
        importers = importers_response.json()

        # Filter the importer data to display only the specified fields
        filtered_importers = [
            {
                'stationName': importer['stationName'],
                'stationType': importer['stationType'],
                'distanceToArrival': importer['distanceToArrival'],
                'maxLandingPadSize': importer['maxLandingPadSize'],
                'systemName': importer['systemName'],
                'sellPrice': importer['sellPrice'],
                'demand': importer['demand'],
                'updatedAt': time_ago(importer['updatedAt']) if 'updatedAt' in importer else None
            }
            for importer in importers
        ]
        
        # Display the filtered importers data in a table
        st.table(filtered_importers)
