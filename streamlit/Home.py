import json
import requests
import time
import streamlit as st
import pandas as pd
import pytz  # Add this import for time zone conversion

nodeId = "01967419-599d-7721-91d2-3ab6693ef38f"
apiKey = "828bb52efa0325b6a580c734c800721b3e5f4fbe34e24f45c83b9c86a3e2cd67"


def anedya_config(NODE_ID, API_KEY):
    global nodeId, apiKey
    nodeId = NODE_ID
    apiKey = API_KEY


def anedya_sendCommand(COMMAND_NAME, COMMAND_DATA):

    url = "https://api.anedya.io/v1/commands/send"
    apiKey_in_formate = "Bearer " + apiKey

    commandExpiry_time = int(time.time() + 518400) * 1000

    payload = json.dumps(
        {
            "nodeid": nodeId,
            "command": COMMAND_NAME,
            "data": COMMAND_DATA,
            "type": "string",
            "expiry": commandExpiry_time,
        }
    )
    headers = {"Content-Type": "application/json", "Authorization": apiKey_in_formate}

    requests.request("POST", url, headers=headers, data=payload)

    # print(response.text)
    # st.write(response.text)


def anedya_setValue(KEY, VALUE):
    url = "https://api.anedya.io/v1/valuestore/setValue"
    apiKey_in_formate = "Bearer " + apiKey

    payload = json.dumps({
        "namespace": {
            "scope": "node",
            "id": nodeId
        },
        "key": KEY,
        "value": VALUE,
        "type": "boolean"
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": apiKey_in_formate
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    # print(response.status_code)
    # print(payload)
    print(response.text)
    return response


def anedya_getValue(KEY):
    url = "https://api.anedya.io/v1/valuestore/getValue"
    apiKey_in_formate = "Bearer " + apiKey

    payload = json.dumps({
        "namespace": {
            "scope": "node",
            "id": nodeId
        },
        "key": KEY
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": apiKey_in_formate
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    responseMessage = response.text
    print(responseMessage)
    errorCode = json.loads(responseMessage).get("errorcode")
    if errorCode == 0:
        data = json.loads(responseMessage).get("value")
        value = [data, 1]
    else:
        print(responseMessage)
        # st.write("No previous value!!")
        value = [False, -1]

    return value


@st.cache_data(ttl=30, show_spinner=False)
def fetchHumidityData() -> pd.DataFrame:
    url = "https://api.anedya.io/v1/aggregates/variable/byTime"
    apiKey_in_formate = "Bearer " + apiKey

    currentTime = int(time.time())
    pastHour_Time = int(currentTime - 86400)

    payload = json.dumps(
        {
            "variable": "humidity",
            "from": pastHour_Time,
            "to": currentTime,
            "config": {
                "aggregation": {
                    "compute": "avg",
                    "forEachNode": True
                },
                "interval": {
                    "measure": "minute",
                    "interval": 5
                },
                "responseOptions": {
                    "timezone": "UTC"
                },
                "filter": {
                    "nodes": [
                        nodeId
                    ],
                    "type": "include"
                }
            }
        }
    )
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": apiKey_in_formate
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response_message = response.text

        if response.status_code == 200:
            data_list = []

            # Parse JSON string
            response_data = json.loads(response_message).get("data")
            if response_data:
                for timeStamp, value in reversed(response_data.items()):
                    for entry in reversed(value):
                        data_list.append(entry)

                if data_list:
                    st.session_state.CurrentHumidity = round(data_list[0]["aggregate"], 2)
                    df = pd.DataFrame(data_list)
                    # Convert timestamp to datetime and set it as the index
                    df["Datetime"] = pd.to_datetime(df["timestamp"], unit="s")
                    local_tz = pytz.timezone("Asia/Kolkata")  # Change to your local time zone
                    df["Datetime"] = df["Datetime"].dt.tz_localize("UTC").dt.tz_convert(local_tz)
                    df.set_index("Datetime", inplace=True)
                    # Drop the original 'timestamp' column as it's no longer needed
                    df.drop(columns=["timestamp"], inplace=True)
                    # Reset the index to prepare for Altair chart
                    chart_data = df.reset_index()
                    return chart_data
        
        # If we get here, either response was not 200, data_list was empty, or response_data was None
        print(f"No humidity data available. Status code: {response.status_code}")
        return pd.DataFrame()
    
    except Exception as e:
        print(f"Error fetching humidity data: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=30, show_spinner=False)
def fetchTemperatureData() -> pd.DataFrame:
    url = "https://api.anedya.io/v1/aggregates/variable/byTime"
    apiKey_in_formate = "Bearer " + apiKey

    currentTime = int(time.time())
    pastHour_Time = int(currentTime - 86400)

    payload = json.dumps(
        {
            "variable": "temperature",
            "from": pastHour_Time,
            "to": currentTime,
            "config": {
                "aggregation": {
                    "compute": "avg",
                    "forEachNode": True
                },
                "interval": {
                    "measure": "minute",
                    "interval": 5
                },
                "responseOptions": {
                    "timezone": "UTC"
                },
                "filter": {
                    "nodes": [
                        nodeId
                    ],
                    "type": "include"
                }
            }
        }
    )
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": apiKey_in_formate
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response_message = response.text

        if response.status_code == 200:
            data_list = []

            # Parse JSON string
            response_data = json.loads(response_message).get("data")
            if response_data:
                for timeStamp, value in reversed(response_data.items()):
                    for entry in reversed(value):
                        data_list.append(entry)

                if data_list:
                    st.session_state.CurrentTemperature = round(data_list[0]["aggregate"], 2)
                    df = pd.DataFrame(data_list)
                    df["Datetime"] = pd.to_datetime(df["timestamp"], unit="s")
                    local_tz = pytz.timezone("Asia/Kolkata")  # Change to your local time zone
                    df["Datetime"] = df["Datetime"].dt.tz_localize("UTC").dt.tz_convert(local_tz)
                    df.set_index("Datetime", inplace=True)
                    # Drop the original 'timestamp' column as it's no longer needed
                    df.drop(columns=["timestamp"], inplace=True)
                    # Reset the index to prepare for Altair chart
                    chart_data = df.reset_index()
                    return chart_data
        
        # If we get here, either response was not 200, data_list was empty, or response_data was None
        print(f"No temperature data available. Status code: {response.status_code}")
        return pd.DataFrame()
    
    except Exception as e:
        print(f"Error fetching temperature data: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=30, show_spinner=False)
def fetchMoistureData() -> pd.DataFrame:
    url = "https://api.anedya.io/v1/aggregates/variable/byTime"
    apiKey_in_formate = "Bearer " + apiKey

    currentTime = int(time.time())
    pastHour_Time = int(currentTime - 86400)

    payload = json.dumps(
        {
            "variable": "moisture",
            "from": pastHour_Time,
            "to": currentTime,
            "config": {
                "aggregation": {
                    "compute": "avg",
                    "forEachNode": True
                },
                "interval": {
                    "measure": "minute",
                    "interval": 5
                },
                "responseOptions": {
                    "timezone": "UTC"
                },
                "filter": {
                    "nodes": [
                        nodeId
                    ],
                    "type": "include"
                }
            }
        }
    )
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": apiKey_in_formate
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response_message = response.text

        if response.status_code == 200:
            data_list = []

            # Parse JSON string
            response_data = json.loads(response_message).get("data")
            if response_data:
                for timeStamp, value in reversed(response_data.items()):
                    for entry in reversed(value):
                        data_list.append(entry)

                if data_list:
                    st.session_state.CurrentMoisture = round(data_list[0]["aggregate"], 2)
                    df = pd.DataFrame(data_list)
                    # Convert timestamp to datetime and set it as the index
                    df["Datetime"] = pd.to_datetime(df["timestamp"], unit="s")
                    local_tz = pytz.timezone("Asia/Kolkata")  # Change to your local time zone
                    df["Datetime"] = df["Datetime"].dt.tz_localize("UTC").dt.tz_convert(local_tz)
                    df.set_index("Datetime", inplace=True)
                    # Drop the original 'timestamp' column as it's no longer needed
                    df.drop(columns=["timestamp"], inplace=True)
                    # Reset the index to prepare for Altair chart
                    chart_data = df.reset_index()
                    return chart_data
        
        # If we get here, either response was not 200, data_list was empty, or response_data was None
        print(f"No moisture data available. Status code: {response.status_code}")
        return pd.DataFrame()
    
    except Exception as e:
        print(f"Error fetching moisture data: {str(e)}")
        return pd.DataFrame()
