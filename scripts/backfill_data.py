import mysql.connector
import src.utils.data_reader as data_reader

conn = mysql.connector.connect(
    host="127.0.0.1", user="root", password="root", database="circa", port=3306
)

def backfill_enphase_15min_datafiles(conn, cursor):
    '''
    Docstring for backfill_enphase_15min_datafiles

    :param conn: Description
    :param cursor: Description
    '''

    enphase_15min_data = data_reader.read_enphase_15min_data_file(
        "data/sample/enphase", "15mins_Oct_2024_Aug_2025.csv", True, "%m/%d/%Y %H:%M"
    )

    # Check for NaN values
    nan_counts = enphase_15min_data.isna().sum()
    if nan_counts.any():
        print(f"Columns with NaN values before filling:")
        print(nan_counts[nan_counts > 0])

    # Fill ALL remaining NaN values with 0
    enphase_15min_data = enphase_15min_data.fillna(0)

    # Verify no NaN values remain
    if enphase_15min_data.isna().any().any():
        print("WARNING: Some NaN values still remain!")
    else:
        print("All NaN values filled successfully")

    # Reset index after dropping rows
    enphase_15min_data = enphase_15min_data.reset_index(drop=False)

    print(f"Total rows to insert: {len(enphase_15min_data)}")

    sql = """
        INSERT INTO enphase (
            date,
            energy_produced,
            energy_consumed,
            grid_exported,
            grid_imported
            )
            VALUES (%s, %s, %s, %s, %s)
        """

    for i, row in enphase_15min_data.iterrows():
        try:
            data = (
                str(row["Date"]),
                float(row["Energy Produced (Wh)"]),
                float(row["Energy Consumed (Wh)"]),
                float(row["Exported to Grid (Wh)"]),
                float(row["Imported from Grid (Wh)"]),
            )
            cursor.execute(sql, data)
            print("Row inserted: ", i)
        except Exception as e:
            print(f"Error inserting row {i}: {e}")
            print(f"Data values: {data}")
            raise

    conn.commit()
    print("Enphase data inserted into MySQL")


def backfill_enphase_panel_data_files(conn, cursor):
    '''
    Docstring for backfill_enphase_panel_data_files

    :param conn: Description
    :param cursor: Description
    '''

    enphase_panel_data = data_reader.read_enphase_panel_data_file(
        "data/sample/enphase", "enphase_daily_Feb23_Sep24_module.csv", True
    )
    enphase_panel_data.reset_index(inplace=True)
    enphase_panel_data["id"] = enphase_panel_data.index + 1

    # Drop rows with invalid timestamps first
    print(f"Rows before dropping invalid timestamps: {len(enphase_panel_data)}")
    enphase_panel_data = enphase_panel_data.dropna(subset=["Date"])
    print(f"Rows after dropping invalid timestamps: {len(enphase_panel_data)}")

    # Check for NaN values
    nan_counts = enphase_panel_data.isna().sum()
    if nan_counts.any():
        print(f"Columns with NaN values before filling:")
        print(nan_counts[nan_counts > 0])

    # Fill ALL remaining NaN values with 0
    enphase_panel_data = enphase_panel_data.fillna(0)

    # Verify no NaN values remain
    if enphase_panel_data.isna().any().any():
        print("WARNING: Some NaN values still remain!")
    else:
        print("All NaN values filled successfully")

    # Reset index after dropping rows
    enphase_panel_data = enphase_panel_data.reset_index(drop=True)
    enphase_panel_data["id"] = enphase_panel_data.index + 1

    print(f"Total rows to insert: {len(enphase_panel_data)}")
    print(f"Sample timestamp: {enphase_panel_data['Date'].iloc[0]}")

    sql = """
        INSERT INTO enphase_panel_production (
            panel_id,
            date,
            production,
            panel_group
            )
            VALUES (%s, %s, %s, %s)
        """

    print(enphase_panel_data.head())

    for column_name in enphase_panel_data.columns:
        if column_name == "id" or column_name == "Date" or column_name == "Total":
            continue
        else:
            panel_group = column_name.split("_")[1]

            for i, row in enphase_panel_data[column_name].items():
                date = enphase_panel_data["Date"].iloc[i].date()
                data = (column_name, date, float(row), panel_group)

                cursor.execute(sql, data)
                print("Row inserted: ", data)

    conn.commit()
    print("Enphase panel data inserted into MySQL")



def backfill_kaatru_weather_data_files(conn, cursor):
    weather_data = data_reader.read_weather_kaatru_data_directory(
        "data/sample/weather/kaatru"
    )

    # Check for NaN values
    nan_counts = weather_data.isna().sum()
    if nan_counts.any():
        print(f"Columns with NaN values before filling:")
        print(nan_counts[nan_counts > 0])

    # Fill ALL remaining NaN values with 0
    weather_data = weather_data.fillna(0)

    # Convert value.sNoxI column to float, setting string values to 0
    weather_data["value.sNoxI"] = pd.to_numeric(weather_data["value.sNoxI"], errors='coerce').fillna(0)

    # Verify no NaN values remain
    if weather_data.isna().any().any():
        print("WARNING: Some NaN values still remain!")
    else:
        print("All NaN values filled successfully")

    # Reset index to make datetime a column instead of dropping it
    weather_data = weather_data.reset_index()

    print(f"Total rows to insert: {len(weather_data)}")

    sql = """
        INSERT INTO kaatru_weather (
            srv_time,
            filename,
            pID,
            dID,
            rHeap,
            lHeap,
            device_timestamp,
            device_uptime,
            latitude,
            ns_orientation,
            longitude,
            ew_orientation,
            altitude,
            speed_over_ground,
            course_over_ground,
            horizontal_dilution_precision,
            acceleration_x,
            acceleration_y,
            acceleration_z,
            gyro_x,
            gyro_y,
            gyro_z,
            accelerometer_temp,
            packetID_arduino,
            arduino_uptime,
            temperature,
            relative_humidity,
            wind_speed,
            rain,
            pm1,
            pm2,
            pm4,
            pm10,
            npm_p5,
            npm_1,
            npm_2,
            npm_4,
            npm_10,
            typical_partical_size,
            temperature_sen55,
            relative_humidity_sen55,
            volatile_organic_compound,
            nox_compounds,
            sunlight_sensor_1_light,
            sunlight_sensor_2_ir,
            sunlight_sensor_3_uv,
            input_voltage,
            fan_tachometer,
            pid_state,
            buzzer_state,
            setpoint,
            fan_pwm,
            min_rpm,
            max_rpm
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

    for i, row in weather_data.iterrows():
        try:
            data = (
                str(row["datetime"]),
                str(row["filename"]),
                int(row["value.pID"]),
                str(row["value.dID"]),
                int(row["value.rHeap"]),
                int(row["value.lHeap"]),
                int(row["value.dTS"]),
                int(row["value.dUT"]),
                float(row["value.lat"]),
                str(row["value.nso"]),
                float(row["value.lon"]),
                str(row["value.ewo"]),
                float(row["value.alt"]),
                float(row["value.sog"]),
                float(row["value.cog"]),
                float(row["value.hdop"]),
                float(row["value.ax"]),
                float(row["value.ay"]),
                float(row["value.az"]),
                float(row["value.gx"]),
                float(row["value.gy"]),
                float(row["value.gz"]),
                float(row["value.accTemp"]),
                int(row["value.pIDar"]),
                int(row["value.aUT"]),
                float(row["value.temp"]),
                float(row["value.rh"]),
                float(row["value.wSpeed"]),
                float(row["value.rain"]),
                float(row["value.sPM1"]),
                float(row["value.sPM2"]),
                float(row["value.sPM4"]),
                float(row["value.sPM10"]),
                float(row["value.sNPMp5"]),
                float(row["value.sNPM1"]),
                float(row["value.sNPM2"]),
                float(row["value.sNPM4"]),
                float(row["value.sNPM10"]),
                float(row["value.sTPS"]),
                float(row["value.sTemp"]),
                float(row["value.sRh"]),
                int(row["value.sVocI"]),
                float(row["value.sNoxI"]),
                int(row["value.aTd0"]),
                int(row["value.aTd1"]),
                int(row["value.aTd2"]),
                int(row["value.a12V"]),
                int(row["value.aFanTacho"]),
                int(row["value.pidState"]),
                int(row["value.BuzzerState"]),
                int(row["value.setpoint"]),
                int(row["value.FanPWM"]),
                int(row["value.minRpm"]),
                int(row["value.maxRpm"])
            )

            cursor.execute(sql, data)
            print("Row inserted: ", i)
        except Exception as e:
            print(f"Error inserting row {i}: {e}")
            raise

    conn.commit()
    print("Kaatru weather data inserted into MySQL")


def backfill_open_weather_data_files(conn, cursor):
    weather_data = data_reader.read_open_weather_data_file(
        "data/sample/weather/open_weather",
        "FormulaHouse-Jan2023-Sep2024.csv",
        set_index=True,
        filter_columns=False,
    )
    weather_data.drop(columns=["dt_iso"], inplace=True)

    weather_data.reset_index(inplace=True)
    weather_data["id"] = weather_data.index + 1

    # Drop rows with invalid timestamps first
    print(f"Rows before dropping invalid timestamps: {len(weather_data)}")
    weather_data = weather_data.dropna(subset=["dt"])
    print(f"Rows after dropping invalid timestamps: {len(weather_data)}")

    # Check for NaN values
    nan_counts = weather_data.isna().sum()
    if nan_counts.any():
        print(f"Columns with NaN values before filling:")
        print(nan_counts[nan_counts > 0])

    # Fill ALL remaining NaN values with 0
    weather_data = weather_data.fillna(0)

    # Verify no NaN values remain
    if weather_data.isna().any().any():
        print("WARNING: Some NaN values still remain!")
    else:
        print("All NaN values filled successfully")

    print(f"Total rows to insert: {len(weather_data)}")
    print(f"Sample timestamp: {weather_data['dt'].iloc[0]}")
    print(weather_data.columns)

    sql = """
        INSERT INTO open_weather (
            date_time,
            timezone,
            city_name,
            latitude,
            longitude,
            temperature,
            visibility,
            dew_point,
            feels_like_temperature,
            temperature_min,
            temperature_max,
            pressure,
            sea_level,
            ground_level,
            humidity,
            wind_speed,
            wind_degree,
            wind_gust,
            rain_1h,
            rain_3h,
            snow_1h,
            snow_3h,
            clouds_all,
            weather_id,
            weather_main,
            weather_description,
            weather_icon
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

    for i, row in weather_data.iterrows():
        try:
            data = (
                str(row["dt"]),
                int(row["timezone"]),
                str(row["city_name"]),
                float(row["lat"]),
                float(row["lon"]),
                float(row["temp"]),
                float(row["visibility"]),
                float(row["dew_point"]),
                float(row["feels_like"]),
                float(row["temp_min"]),
                float(row["temp_max"]),
                float(row["pressure"]),
                float(row["sea_level"]),
                float(row["grnd_level"]),
                float(row["humidity"]),
                float(row["wind_speed"]),
                int(row["wind_deg"]),
                int(row["wind_gust"]),
                float(row["rain_1h"]),
                float(row["rain_3h"]),
                float(row["snow_1h"]),
                float(row["snow_3h"]),
                int(row["clouds_all"]),
                int(row["weather_id"]),
                str(row["weather_main"]),
                str(row["weather_description"]),
                str(row["weather_icon"])
            )
            cursor.execute(sql, data)
            print("Row inserted: ", i)
        except Exception as e:
            print(f"Error inserting row {i}: {e}")
            raise

    conn.commit()
    print("Open Weather data inserted into MySQL")


def backfill_studer_data_files(conn, cursor):
    cursor = conn.cursor()

    studer_data = data_reader.read_studer_data_directory(
        "data/sample/studer/Studer_Oct2024_Aug_2025", return_raw_data=True, set_index=True
    )
    studer_data.reset_index(inplace=True)

    # Drop rows with invalid timestamps first
    print(f"Rows before dropping invalid timestamps: {len(studer_data)}")
    studer_data = studer_data.dropna(subset=["Timestamp"])
    print(f"Rows after dropping invalid timestamps: {len(studer_data)}")

    # Check for NaN values
    nan_counts = studer_data.isna().sum()
    if nan_counts.any():
        print(f"Columns with NaN values before filling:")
        print(nan_counts[nan_counts > 0])

    # Fill ALL remaining NaN values with 0
    studer_data = studer_data.fillna(0)

    # Verify no NaN values remain
    if studer_data.isna().any().any():
        print("WARNING: Some NaN values still remain!")
    else:
        print("All NaN values filled successfully")

    # Reset index after dropping rows
    studer_data = studer_data.reset_index(drop=True)
    studer_data["id"] = studer_data.index + 1

    print(f"Total rows to insert: {len(studer_data)}")
    print(f"Sample timestamp: {studer_data['Timestamp'].iloc[0]}")

    sql = """
        INSERT INTO studer (
            date_time,
            battery_voltage_l1,
            battery_voltage_l2,
            battery_voltage_l3,
            grid_input_voltage_l1,
            grid_input_voltage_l2,
            grid_input_voltage_l3,
            grid_input_current_l1,
            grid_input_current_l2,
            grid_input_current_l3,
            apparent_power_output_l1,
            apparent_power_output_l2,
            apparent_power_output_l3,
            power_output_w_external_l1,
            power_output_w_external_l2,
            power_output_w_external_l3,
            output_frequency_l1,
            output_frequency_l2,
            output_frequency_l3,
            grid_input_frequency_l1,
            grid_input_frequency_l2,
            grid_input_frequency_l3,
            xt_phase_l1,
            xt_phase_l2,
            xt_phase_l3,
            xt_mode_l1,
            xt_mode_l2,
            xt_mode_l3,
            grid_status_l1,
            grid_status_l2,
            grid_status_l3,
            xt_rme_l1,
            xt_rme_l2,
            xt_rme_l3,
            xt_aux1_l1,
            xt_aux1_l2,
            xt_aux1_l3,
            xt_aux2_l1,
            xt_aux2_l2,
            xt_aux2_l3,
            battery_voltage_l1_1,
            battery_voltage_l2_2,
            battery_voltage_l3_3,
            battery_current_l1,
            battery_current_l2,
            battery_current_l3,
            studer_grid_imp_exp_l1,
            studer_grid_imp_exp_l2,
            studer_grid_imp_exp_l3,
            power_output_l1,
            power_output_l2,
            power_output_l3,
            studer_temperature_l1,
            studer_temperature_l2,
            studer_temperature_l3,
            battery_voltage,
            battery_current,
            battery_state_of_charge,
            battery_temperature,
            solar_power,
            xt_dbg1,
            bsp_loce,
            sys_msg,
            sys_scom_err,
            vt_psom_1,
            vt_psom_all,
            vt_mode,
            vt_tp1m,
            vt_upvm,
            vt_ibam,
            vt_ubam,
            vt_phas,
            vt_rme,
            vt_aux_1,
            vt_aux_2
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

    for i, row in studer_data.iterrows():
        try:
            data = (
                str(row["Timestamp"]),
                float(row["Battery Voltage - L1"]),
                float(row["Battery Voltage - L2"]),
                float(row["Battery Voltage - L3"]),
                float(row["Grid Input Voltage - L1"]),
                float(row["Grid Input Voltage - L2"]),
                float(row["Grid Input Voltage - L3"]),
                float(row["Grid Input Current - L1"]),
                float(row["Grid Input Current - L2"]),
                float(row["Grid Input Current - L3"]),
                float(row["Apparent Power Output - L1"]),
                float(row["Apparent Power Output - L2"]),
                float(row["Apparent Power Output - L3"]),
                float(row["Apparent Power Output w/ External - L1"]),
                float(row["Apparent Power Output w/ External - L2"]),
                float(row["Apparent Power Output w/ External - L3"]),
                float(row["Studer Output Frequency - L1"]),
                float(row["Studer Output Frequency - L2"]),
                float(row["Studer Output Frequency - L3"]),
                float(row["Grid Input Frequency - L1"]),
                float(row["Grid Input Frequency - L2"]),
                float(row["Grid Input Frequency - L3"]),
                float(row["XT-Phase - L1"]),
                float(row["XT-Phase - L2"]),
                float(row["XT-Phase - L3"]),
                int(row["XT-Mode - L1"]),
                int(row["XT-Mode - L2"]),
                int(row["XT-Mode - L3"]),
                int(row["Studer Grid Status - L1"]),
                int(row["Studer Grid Status - L2"]),
                int(row["Studer Grid Status - L3"]),
                int(row["XT-RME - L1"]),
                int(row["XT-RME - L2"]),
                int(row["XT-RME - L3"]),
                int(row["XT-AUX1 - L1"]),
                int(row["XT-AUX1 - L2"]),
                int(row["XT-AUX1 - L3"]),
                int(row["XT-AUX2 - L1"]),
                int(row["XT-AUX2 - L2"]),
                int(row["XT-AUX2 - L3"]),
                float(row["Battery Voltage - L1-1"]),
                float(row["Battery Voltage - L2-2"]),
                float(row["Battery Voltage - L3-3"]),
                float(row["Battery Current - L1-1"]),
                float(row["Battery Current - L2-2"]),
                float(row["Battery Current - L3-3"]),
                float(row["Studer Grid Net Export/Import - L1-1"]),
                float(row["Studer Grid Net Export/Import - L2-2"]),
                float(row["Studer Grid Net Export/Import - L3-3"]),
                float(row["Power Output - L1-1"]),
                float(row["Power Output - L2-2"]),
                float(row["Power Output - L3-3"]),
                float(row["Studer Temperature - L1-1"]),
                float(row["Studer Temperature - L2-2"]),
                float(row["Studer Temperature - L3-3"]),
                float(row["Battery Voltage"]),
                float(row["Battery Current"]),
                float(row["Battery State of Charge"]),
                float(row["Battery Internal Temperature"]),
                float(row["Solar Power"]),
                float(row["Dev XT-DBG1"]),
                float(row["Dev BSP-locE"]),
                float(row["Dev Sys MSG"]),
                float(row["Dev Sys SCOM Err"]),
                float(row["VT-PsoM - 1"]),
                float(row["VT-PsoM - All"]),
                float(row["VT-Mode"]),
                float(row["VT-Tp1M"]),
                float(row["VT-UpvM"]),
                float(row["VT-IbaM"]),
                float(row["VT-UbaM"]),
                float(row["VT-Phas"]),
                float(row["VT-RME"]),
                float(row["VT-AUX1"]),
                float(row["VT-AUX2"])
            )
            cursor.execute(sql, data)
            print("Row inserted: ", i)
        except Exception as e:
            print(f"Error inserting row {i}: {e}")
            print(f"Data values: {data}")
            raise

    conn.commit()
    print("Studer data inserted into MySQL")
