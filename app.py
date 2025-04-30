import math
import pandas as pd
import streamlit as st

# ---- Cable Properties (Copper only for now) ----
cable_data = {
    "1.5": {"resistance": 12.1, "rating": 18},
    "2.5": {"resistance": 7.41, "rating": 24},
    "4": {"resistance": 4.61, "rating": 32},
    "6": {"resistance": 3.08, "rating": 41},
    "10": {"resistance": 1.83, "rating": 57},
    "16": {"resistance": 1.15, "rating": 76},
    "25": {"resistance": 0.727, "rating": 101},
    "35": {"resistance": 0.524, "rating": 125},
}

# ---- Streamlit UI ----
st.title("Street Lighting Cable Sizing Tool")
st.write("Calculate suitable cable size and voltage drop for street lighting.")

voltage = st.selectbox("System Voltage (V)", [230, 400])
load_per_pole = st.number_input("Load per Pole (Watts)", min_value=1.0)
number_of_poles = st.number_input("Number of Poles", min_value=1, step=1)
pole_spacing = st.number_input("Pole Spacing (meters)", min_value=1.0)
power_factor = st.slider("Power Factor", 0.1, 1.0, 0.9)
cable_material = st.selectbox("Cable Material", ['copper', 'aluminum'])
voltage_drop_limit_percent = st.slider("Allowable Voltage Drop (%)", 1.0, 10.0, 5.0)

if st.button("Calculate"):
    total_load_watt = load_per_pole * number_of_poles
    current = total_load_watt / (voltage * power_factor)
    cable_length = pole_spacing * (number_of_poles - 1)

    results = []
    selected_size = None

    for size, props in cable_data.items():
        resistance_ohm_per_km = props['resistance']
        voltage_drop = (2 * resistance_ohm_per_km * cable_length / 1000) * current
        voltage_drop_percent = (voltage_drop / voltage) * 100
        is_suitable = voltage_drop_percent <= voltage_drop_limit_percent and current <= props['rating']

        results.append({
            "Cable Size (mm²)": size,
            "Resistance (Ohm/km)": resistance_ohm_per_km,
            "Current Rating (A)": props['rating'],
            "Voltage Drop (V)": round(voltage_drop, 2),
            "Voltage Drop (%)": round(voltage_drop_percent, 2),
            "Suitable": is_suitable
        })

        if is_suitable and not selected_size:
            selected_size = size

    st.subheader("Sizing Summary")
    st.write(f"**Total Load:** {total_load_watt:.2f} W")
    st.write(f"**Estimated Current:** {current:.2f} A")
    st.write(f"**Cable Length:** {cable_length:.2f} m")

    if selected_size:
        st.success(f"Suggested Cable Size: {selected_size} mm²")
    else:
        st.error("No suitable cable size found within voltage drop and current limits.")

    df = pd.DataFrame(results)
    st.dataframe(df)

    # Export to Excel
    output_file = "cable_sizing_results.xlsx"
    df.to_excel(output_file, index=False)
    with open(output_file, "rb") as file:
        st.download_button("Download Excel Report", file, file_name=output_file)
