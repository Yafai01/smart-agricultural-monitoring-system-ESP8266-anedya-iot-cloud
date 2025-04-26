import streamlit as st
import pandas as pd
import altair as alt
from streamlit_autorefresh import st_autorefresh

from utils.anedya import anedya_config
from utils.anedya import anedya_sendCommand
from utils.anedya import anedya_getValue
from utils.anedya import anedya_setValue
from utils.anedya import fetchHumidityData
from utils.anedya import fetchTemperatureData
from utils.anedya import fetchMoistureData

nodeId = "157743b8-3975-11ef-9ecc-a1461caa74a3"  # get it from anedya dashboard -> project -> node 
apiKey = "a97a55bb0925ad628f6d2c4d7664f4b0919e198e2720504d2c02901dc7387408"  # aneyda project apikey

st.set_page_config(page_title="Dashboard", layout="wide")


st_autorefresh(interval=10000, limit=None, key="auto-refresh-handler")

# --------------- HELPER FUNCTIONS -----------------------


def V_SPACE(lines):
    for _ in range(lines):
        st.write("&nbsp;")


humidityData = pd.DataFrame()
temperatureData = pd.DataFrame()
moistureData = pd.DataFrame()

def main():

    anedya_config(nodeId, apiKey)
    global humidityData, temperatureData, moistureData

    # Initialize the log in state if does not exist
    if "LoggedIn" not in st.session_state:
        st.session_state.LoggedIn = False

    if "CurrentHumidity" not in st.session_state:
        st.session_state.CurrentHumidity = 0

    if "CurrentTemperature" not in st.session_state:
        st.session_state.CurrentTemperature = 0
    
    if "CurrentMoisture" not in st.session_state:
        st.session_state.CurrentMoisture = 0

    if st.session_state.LoggedIn is False:
        drawLogin()
    else:
        humidityData = fetchHumidityData()
        temperatureData = fetchTemperatureData()
        moistureData = fetchMoistureData()

        drawDashboard()


def drawLogin():
    cols = st.columns([1, 0.8, 1], gap='small')
    with cols[0]:
        pass
    with cols[1]:
        st.title("Smart Agriculture Dashboard", anchor=False)
        username_inp = st.text_input("Username")
        password_inp = st.text_input("Password", type="password")
        submit_button = st.button(label="Submit")

        if submit_button:
            if username_inp == "qwerty" and password_inp == "987654":
                st.session_state.LoggedIn = True
                st.rerun()
            else:
                st.error("Invalid Credential!")
    with cols[2]:
        print()


def drawDashboard():
    headercols = st.columns([1, 0.1, 0.1], gap="small")
    with headercols[0]:
        st.title("Anedya Dashboard by Dhruv", anchor=False)
    with headercols[1]:
        st.button("Refresh")
    with headercols[2]:
        logout = st.button("Logout")

    if logout:
        st.session_state.LoggedIn = False
        st.rerun()

    st.markdown("This dashboard provides live view of the Farm")

    st.subheader(body="Current Status", anchor=False)
    cols = st.columns(3, gap="medium")
    with cols[0]:
        st.metric(label="Humidity", value=str(st.session_state.CurrentHumidity) + " %")
    with cols[1]:
        st.metric(label="Temperature", value=str(st.session_state.CurrentTemperature) + "  °C")
    with cols[2]:
        st.metric(label="Moisture", value=str(st.session_state.CurrentMoisture))    
    # with cols[3]:
    #    st.metric(label="Refresh Count", value=count)

    charts = st.columns(1, gap="small")
    with charts[0]:
        st.subheader(body="Humidity ", anchor=False)
        if humidityData.empty:
            st.write("No Data Available!")
        else:
            humidity_chart_an = alt.Chart(data=humidityData).mark_area(
                line={'color': '#1fff7c'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#1fff7c', offset=1),
                        alt.GradientStop(color='rgba(255,255,255,0)', offset=0)],
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0,
                ),
                interpolate='monotone',
                cursor='crosshair'
            ).encode(
                x=alt.X(
                    shorthand="Datetime:T",
                    axis=alt.Axis(format="%Y-%m-%d %H:%M:%S", title="Datetime", tickCount=10, grid=True, tickMinStep=5),
                ),  # T indicates temporal (time-based) data
                y=alt.Y(
                    "aggregate:Q",
                    scale=alt.Scale(domain=[0, 100]),
                    axis=alt.Axis(title="Humidity (%)", grid=True, tickCount=10),
                ),  # Q indicates quantitative data
                tooltip=[alt.Tooltip('Datetime:T', format="%Y-%m-%d %H:%M:%S", title="Time",),
                        alt.Tooltip('aggregate:Q', format="0.2f", title="Value")],
            ).properties(height=400).interactive()

            # Display the Altair chart using Streamlit
            st.altair_chart(humidity_chart_an, use_container_width=True)


    charts = st.columns(1, gap="small")  # Create a new column

    with charts[0]:
        st.subheader(body="Temperature", anchor=False)
        if temperatureData.empty:
            st.write("No Data Available!")
        else:
            temperature_chart_an = alt.Chart(data=temperatureData).mark_area(
                line={'color': '#ff1f32'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#ff1f32', offset=1),
                        alt.GradientStop(color='rgba(255,255,255,0)', offset=0)],
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0,
                ),
                interpolate='monotone',
                cursor='crosshair'
            ).encode(
                x=alt.X(
                    shorthand="Datetime:T",
                    axis=alt.Axis(format="%Y-%m-%d %H:%M:%S", title="Datetime", tickCount=10, grid=True, tickMinStep=5),
                ),  # T indicates temporal (time-based) data
                y=alt.Y(
                    "aggregate:Q",
                    # scale=alt.Scale(domain=[0, 100]),
                    scale=alt.Scale(zero=False, domain=[10, 50]),
                    axis=alt.Axis(title="Temperature (°C)", grid=True, tickCount=10),
                ),  # Q indicates quantitative data
                tooltip=[alt.Tooltip('Datetime:T', format="%Y-%m-%d %H:%M:%S", title="Time",),
                        alt.Tooltip('aggregate:Q', format="0.2f", title="Value")],
            ).properties(height=400).interactive()

            st.altair_chart(temperature_chart_an, use_container_width=True)


    charts = st.columns(1, gap="small")  # Create a new column

    with charts[0]:
        st.subheader(body="Moisture ", anchor=False)
        if moistureData.empty:
            st.write("No Data Available!")
        else:
            moisture_chart_an = alt.Chart(data=moistureData).mark_area(
                line={'color': '#1fa2ff'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#1fa2ff', offset=1),
                        alt.GradientStop(color='rgba(255,255,255,0)', offset=0)],
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0,
                ),
                interpolate='monotone',
                cursor='crosshair'
            ).encode(
                x=alt.X(
                    shorthand="Datetime:T",
                    axis=alt.Axis(format="%Y-%m-%d %H:%M:%S", title="Datetime", tickCount=10, grid=True, tickMinStep=5),
                ),  # T indicates temporal (time-based) data
                y=alt.Y(
                    "aggregate:Q",
                    scale=alt.Scale(domain=[0, 1100]),
                    axis=alt.Axis(title="Moisture", grid=True, tickCount=10),
                ),  # Q indicates quantitative data
                tooltip=[alt.Tooltip('Datetime:T', format="%Y-%m-%d %H:%M:%S", title="Time",),
                        alt.Tooltip('aggregate:Q', format="0.2f", title="Value")],
            ).properties(height=400).interactive()

            # Display the Altair chart using Streamlit
            st.altair_chart(moisture_chart_an, use_container_width=True)


if __name__ == "__main__":
    main()
