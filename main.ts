//  tham số "data" tượng trưng cho dữ liệu cần xử lý
//  dữ liệu xử lý bằng cách bỏ đuôi sau dấu "#" (bao gồm cả #)
function process_data(data: string) {
    
    if (data.includes("#331")) {
        temp_air = parseFloat(data.substr(0, data.length - 4))
    } else if (data.includes("#415")) {
        wifi_data[1] = data.substr(0, data.length - 4)
    } else if (data.includes("#417")) {
        wifi_data[0] = data.substr(0, data.length - 4)
    }
    
}

bluetooth.onBluetoothConnected(function on_bluetooth_connected() {
    
    connect = true
})
//  hàm send_data có hai tham số là h và t tượng trưng cho:
//  h = humidity
//  t = temperature
function send_data(h: number, t: number) {
    esp8266.uploadThingspeak("2WWRE6MHVGBS1Q7S", h, t)
    if (esp8266.isThingspeakUploaded()) {
        basic.showIcon(IconNames.Yes)
        basic.clearScreen()
    } else {
        basic.showIcon(IconNames.No)
        basic.clearScreen()
    }
    
}

function sensor_door(digiht: number) {
    if (user_status == "user leave" && digiht == 1) {
        music.ringTone(349)
        esp8266.sendTelegramMessage("", "", "theft warning")
    } else {
        music.stopAllSounds()
    }
    
}

bluetooth.onUartDataReceived(serial.delimiters(Delimiters.Hash), function on_uart_data_received() {
    
    while (connect) {
        data2 = bluetooth.uartReadUntil(serial.delimiters(Delimiters.Hash))
        if (data2 == "gate_open") {
            
        } else if (data2 == "gate_close") {
            
        } else if (data2 == "user_leave") {
            user_status = "user leave"
        } else {
            process_data(data2)
        }
        
    }
})
function DHT22() {
    dht11_dht22.queryData(DHTtype.DHT22, DigitalPin.P0, true, false, true)
    if (dht11_dht22.sensorrResponding() && dht11_dht22.readDataSuccessful()) {
        OLED12864_I2C.showString(0, 0, "smarthome micro:bit v6.8.3", 1)
        OLED12864_I2C.showString(0, 1, "device name: " + control.deviceName(), 1)
        OLED12864_I2C.showString(0, 2, "device serial: " + ("" + control.deviceSerialNumber()), 1)
        basic.pause(2000)
        OLED12864_I2C.clear()
    } else {
        OLED12864_I2C.showString(0, 0, "Sensor DHT22 is not found. Please check and reboot system", 1)
        esp8266.sendTelegramMessage("", "", "Sensor DHT22 is not found. Please check and reboot system")
        dht11_dht22.queryData(DHTtype.DHT22, DigitalPin.P0, true, false, true)
        control.reset()
    }
    
}

function start() {
    
    pins.setAudioPin(AnalogPin.P3)
    temp_air = temp_air
    list2 = [0, 0]
    wifi_data = [wifi_data[0], wifi_data[1]]
    NFC.NFC_setSerial(SerialPin.P16, SerialPin.P15)
    connect = false
    keypad.setKeyPad3(DigitalPin.P10, DigitalPin.P11, DigitalPin.P12, DigitalPin.P13, DigitalPin.P14, DigitalPin.P15, DigitalPin.P16)
    OLED12864_I2C.init(60)
    OLED12864_I2C.invert(false)
    OLED12864_I2C.zoom(false)
    OLED12864_I2C.on()
    bluetooth.startAccelerometerService()
    bluetooth.startButtonService()
    bluetooth.startIOPinService()
    bluetooth.startLEDService()
    bluetooth.startTemperatureService()
    bluetooth.startMagnetometerService()
    WIFI()
}

function WIFI() {
    esp8266.init(SerialPin.P16, SerialPin.P15, BaudRate.BaudRate115200)
    if (esp8266.isESP8266Initialized()) {
        esp8266.connectWiFi(wifi_data[0], wifi_data[1])
        if (esp8266.isWifiConnected()) {
            DHT22()
        } else {
            OLED12864_I2C.showString(0, 0, "can't connect to router, plaese check your router, module and reboot system", 1)
            esp8266.connectWiFi(wifi_data[0], wifi_data[1])
            esp8266.sendTelegramMessage("", "", "can't connect to router, plaese check your router, module and reboot system")
            control.reset()
        }
        
    } else {
        OLED12864_I2C.showString(0, 0, "wifi module esp8266 is not found. Please check and reboot system", 1)
        esp8266.init(SerialPin.P16, SerialPin.P15, BaudRate.BaudRate115200)
        esp8266.connectWiFi(wifi_data[0], wifi_data[1])
        esp8266.sendTelegramMessage("", "", "wifi module esp8266 is not found. Please check and reboot system")
        control.reset()
    }
    
}

let list2 : number[] = []
let data2 = ""
let user_status = ""
let connect = false
let wifi_data : string[] = []
let temp_air = 0
start()
basic.forever(function on_forever() {
    pins.analogWritePin(AnalogPin.P0, pins.analogReadPin(AnalogPin.P1))
    list2[0] = dht11_dht22.readData(dataType.humidity)
    list2[1] = dht11_dht22.readData(dataType.temperature)
    send_data(list2[0], list2[1])
    sensor_door(pins.digitalReadPin(DigitalPin.P0))
})
