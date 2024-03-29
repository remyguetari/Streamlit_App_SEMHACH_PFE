import streamlit as st
import requests
import base64
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

def get_access_token(client_id, client_secret):
    auth_url = "https://digital.iservices.rte-france.com/token/oauth/"
    data = {"grant_type": "client_credentials"}

    credentials = f"{client_id}:{client_secret}"
    credentials_base64 = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {credentials_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(auth_url, data=data, headers=headers)

    if response.status_code == 200:
        access_token_data = response.json()
        return access_token_data.get("access_token")
    else:
        st.error(f"Error fetching access token. Error code: {response.status_code}")

def get_weather_forecast(api_key, lat, lon):
    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        forecast_data = []
        for forecast in data['list']:
            date_time = pd.to_datetime(forecast['dt_txt'])
            temperature = forecast['main']['temp'] - 273
            forecast_data.append({'Date and Time': date_time, 'Temperature (°C)': temperature})

        df = pd.DataFrame(forecast_data)
        return df
    else:
        st.error(f"Error fetching weather data. Error code: {response.status_code}")

def main():
    st.title("Data Visualization PFE APP")
    #st.header("Electricity Exchange Prices in France")
    # Replace 'YOUR_CLIENT_ID' and 'YOUR_CLIENT_SECRET' with your actual values
    client_id = "1e0de31c-6c1a-4166-b0f8-d194bc163b13"
    client_secret = "3cb2bbf9-74ab-45b0-84e4-94d557321d37"

    access_token = get_access_token(client_id, client_secret)

    if access_token:
        today = datetime.now()
        date_format = "%Y-%m-%dT00:00:00+02:00"
        start_date = today.strftime(date_format)
        end_date = (today + timedelta(days=1)).strftime(date_format)

        #st.write(f"Start: {start_date}, End: {end_date}")

        api_url = "https://digital.iservices.rte-france.com/open_api/wholesale_market/v2/france_power_exchanges"
        params = {}

        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(api_url, params=params, headers=headers)

        if response.status_code == 200:
            spot_prices_data = response.json()

            start_dates = [entry['start_date'] for entry in spot_prices_data['france_power_exchanges'][0]['values']]
            prices = [entry['price'] for entry in spot_prices_data['france_power_exchanges'][0]['values']]

            start_dates = [datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z") for date in start_dates]

             # Plot the data
            fig, ax = plt.subplots()
            ax.plot(start_dates, prices, label='Price')
            ax.set_title('Electricity Exchange Prices in France')
            ax.set_xlabel('Date and Time')
            ax.set_ylabel('Price')
            ax.legend()
            
            # Rotate x-axis labels
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
            
            plt.tight_layout()

            # Display the Matplotlib plot in Streamlit
            st.pyplot(fig)
        else:
            st.error(f"Error fetching spot prices. Error code: {response.status_code}")
    else:
        st.error("Access token not found.")
    #st.header("Weather Forecast")
    # Replace 'YOUR_API_KEY', 46.17, and 20.52 with your OpenWeatherMap API key and desired coordinates
    api_key = '1a57c000e6a7972a8115a8e1aef41495'
    lat = 46.17
    lon = 20.52

    weather_df = get_weather_forecast(api_key, lat, lon)

    fig_weather, ax_weather = plt.subplots()
    ax_weather.plot(weather_df['Date and Time'], weather_df['Temperature (°C)'])
    ax_weather.set_title('Weather Forecast for the Next 5 Days')
    ax_weather.set_xlabel('Date and Time')
    ax_weather.set_ylabel('Temperature (°C)')
    plt.tight_layout()
    st.pyplot(fig_weather)

if __name__ == "__main__":
    main()
