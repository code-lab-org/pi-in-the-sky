
var client = new Paho.MQTT.Client("pi-in-the-sky.code-lab.org", 9001, "");

client.connect({
  "onFailure": function(e) {
    console.log(e);
    alert("Error connecting to broker.");
  },
  "onSuccess": function() {
    client.subscribe("pits/#", {
      "onFailure": function(e) {
        console.log(e);
        alert("Error subscribing to topic.");
      }
    });
  }
});

client.onMessageArrived = function(message) {
  if(message.destinationName == "pits/time") {
    $("#time").text(message.payloadString);
  }
  if(message.destinationName == "pits/position") {
    $("#position").text(message.payloadString);
  }
  if(message.destinationName == "pits/active_fires") {
    $("#active_fires").text(message.payloadString);
  }
  if(message.destinationName == "pits/detected_fires") {
    $("#detected_fires").text(message.payloadString);
  }
};