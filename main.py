# tham số "data" tượng trưng cho dữ liệu cần xử lý
# dữ liệu xử lý bằng cách bỏ đuôi sau dấu "#" (bao gồm cả #)
def process_data(data: str):
    global temp_air
    if data.includes("#331"):
        temp_air = parse_float(data.substr(0, len(data) - 4))
    elif data.includes("#415"):
        wifi_data[1] = data.substr(0, len(data) - 4)
    elif data.includes("#417"):
        wifi_data[0] = data.substr(0, len(data) - 4)

def on_bluetooth_connected():
    global connect
    connect = True
bluetooth.on_bluetooth_connected(on_bluetooth_connected)

# hàm send_data có hai tham số là h và t tượng trưng cho:
# h = humidity
# t = temperature
def send_data(h: number, t: number):
    esp8266.upload_thingspeak("2WWRE6MHVGBS1Q7S", h, t)
    if esp8266.is_thingspeak_uploaded():
        basic.show_icon(IconNames.YES)
        basic.clear_screen()
    else:
        basic.show_icon(IconNames.NO)
        basic.clear_screen()
def sensor_door(digiht: number):
    if user_status == "user leave" and digiht == 1:
        music.ring_tone(349)
        esp8266.send_telegram_message("", "", "theft warning")
    else:
        music.stop_all_sounds()

def on_uart_data_received():
    global data2, user_status
    while connect:
        data2 = bluetooth.uart_read_until(serial.delimiters(Delimiters.HASH))
        if data2 == "gate_open":
            pass
        elif data2 == "gate_close":
            pass
        elif data2 == "user_leave":
            user_status = "user leave"
        else:
            process_data(data2)
bluetooth.on_uart_data_received(serial.delimiters(Delimiters.HASH), on_uart_data_received)

def DHT22():
    dht11_dht22.query_data(DHTtype.DHT22, DigitalPin.P0, True, False, True)
    if dht11_dht22.sensorr_responding() and dht11_dht22.read_data_successful():
        OLED12864_I2C.show_string(0, 0, "smarthome micro:bit v6.8.3", 1)
        OLED12864_I2C.show_string(0, 1, "device name: " + control.device_name(), 1)
        OLED12864_I2C.show_string(0,
            2,
            "device serial: " + str(control.device_serial_number()),
            1)
        basic.pause(2000)
        OLED12864_I2C.clear()
    else:
        OLED12864_I2C.show_string(0,
            0,
            "Sensor DHT22 is not found. Please check and reboot system",
            1)
        esp8266.send_telegram_message("",
            "",
            "Sensor DHT22 is not found. Please check and reboot system")
        dht11_dht22.query_data(DHTtype.DHT22, DigitalPin.P0, True, False, True)
        control.reset()
def start():
    global temp_air, list2, wifi_data, connect
    pins.set_audio_pin(AnalogPin.P3)
    temp_air = temp_air
    list2 = [0, 0]
    wifi_data = [wifi_data[0], wifi_data[1]]
    NFC.NFC_setSerial(SerialPin.P16, SerialPin.P15)
    connect = False
    keypad.set_key_pad3(DigitalPin.P10,
        DigitalPin.P11,
        DigitalPin.P12,
        DigitalPin.P13,
        DigitalPin.P14,
        DigitalPin.P15,
        DigitalPin.P16)
    OLED12864_I2C.init(60)
    OLED12864_I2C.invert(False)
    OLED12864_I2C.zoom(False)
    OLED12864_I2C.on()
    bluetooth.start_accelerometer_service()
    bluetooth.start_button_service()
    bluetooth.start_io_pin_service()
    bluetooth.start_led_service()
    bluetooth.start_temperature_service()
    bluetooth.start_magnetometer_service()
    WIFI()
def WIFI():
    esp8266.init(SerialPin.P16, SerialPin.P15, BaudRate.BAUD_RATE115200)
    if esp8266.is_esp8266_initialized():
        esp8266.connect_wi_fi(wifi_data[0], wifi_data[1])
        if esp8266.is_wifi_connected():
            DHT22()
        else:
            OLED12864_I2C.show_string(0,
                0,
                "can't connect to router, plaese check your router, module and reboot system",
                1)
            esp8266.connect_wi_fi(wifi_data[0], wifi_data[1])
            esp8266.send_telegram_message("",
                "",
                "can't connect to router, plaese check your router, module and reboot system")
            control.reset()
    else:
        OLED12864_I2C.show_string(0,
            0,
            "wifi module esp8266 is not found. Please check and reboot system",
            1)
        esp8266.init(SerialPin.P16, SerialPin.P15, BaudRate.BAUD_RATE115200)
        esp8266.connect_wi_fi(wifi_data[0], wifi_data[1])
        esp8266.send_telegram_message("",
            "",
            "wifi module esp8266 is not found. Please check and reboot system")
        control.reset()
list2: List[number] = []
data2 = ""
user_status = ""
connect = False
wifi_data: List[str] = []
temp_air = 0
start()

def on_forever():
    pins.analog_write_pin(AnalogPin.P0, pins.analog_read_pin(AnalogPin.P1))
    list2[0] = dht11_dht22.read_data(dataType.HUMIDITY)
    list2[1] = dht11_dht22.read_data(dataType.TEMPERATURE)
    send_data(list2[0], list2[1])
    sensor_door(pins.digital_read_pin(DigitalPin.P0))
basic.forever(on_forever)
