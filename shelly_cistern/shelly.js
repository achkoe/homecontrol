// ======================================================
// Shelly Plug M Gen3
// Power Supervisor with MQTT Events
// ======================================================


// ---------------- Configuration -----------------------

const DEVICE_ID = "plug_cistern";
const MQTT_TOPIC = "shelly/cistern/events";
const POWER_THRESHOLD = 50;       // Watt
//const T_ON = 35 * 60 * 1000;       // 35 minutes
const T_ON = 0.5 * 60 * 1000;       // 30 seconds
const CHECK_INTERVAL = 10000;      // 10 seconds


// ---------------- internal variables -------------------

let state = "unknown";
let sstate = 0;
let p_on_since = null;

// ------------------------------------------------------
// helpper functions
// ------------------------------------------------------

function unixTime() {
    return Math.floor(Date.now() / 1000);
}


function sendEvent(event, power) {
    try {
      power = Number(power.toFixed(1));
    } catch (error) {
      print(error);
    }
    let payload = {
        device: DEVICE_ID,
        event: event,
        power: power,
        threshold: POWER_THRESHOLD,
        state: state,
        timestamp: unixTime()
    };
    print("B:" + JSON.stringify(payload));
    MQTT.publish(
        MQTT_TOPIC,
        JSON.stringify(payload)
    );

}

// ------------------------------------------------------
// relay control
// ------------------------------------------------------

function switchOn(onoff) {
    Shelly.call("Switch.Set", {id: 0, on: onoff});
    print("Relay " + onoff);
}
// ------------------------------------------------------
// state machine
// ------------------------------------------------------

function processPower(power) {
    let newState = (power >= POWER_THRESHOLD) ? "p_on": "p_off";
    if (state === "unknown") {
        state = newState;
        if (state === "p_on") {
            p_on_since = Date.now();
        }
        return;
    }
    // p_off -> p_on
    if (state === "p_off" && newState === "p_on") {
        state = "p_on";
        p_on_since = Date.now();
        sendEvent("event_on", power);
        sstate = 2;
    }
    // p_on -> p_off
    else if (state === "p_on" && newState === "p_off") {
        state = "p_off";
        p_on_since = null;
        sendEvent("event_off", power);
        sstate = 2;
    }
}

// ------------------------------------------------------
// State Handler
// ------------------------------------------------------

Shelly.addStatusHandler(
    function(status) {
        // print("A:" + JSON.stringify(status));
        if (!status.delta)
            return;
        let power = status.delta.apower;
        processPower(power);
    }
);

// ------------------------------------------------------
// Timer for t_on
// ------------------------------------------------------

Timer.set(
    CHECK_INTERVAL, true, function() {
      
        if (sstate > 0) {
          Shelly.call("Switch.GetStatus", { id: 0 }, function (result, error_code, error_message) {
            if (error_code === 0) {
                    print("Current power: " + result.apower + " W");
                    sendEvent(state, result.apower);
                }
          });
          sstate -= 1;
        }
      
        if (state !== "p_on")
            return;
        if (p_on_since === null)
            return;
        if ((Date.now() - p_on_since) >= T_ON) {
            sendEvent("disable", 0);
            switchOn(false);
            // deactivate forever
            p_on_since = null;
        }
    }
);
// ------------------------------------------------------
// Start
// ------------------------------------------------------

switchOn(true);
print("Shelly Power Monitor startet");