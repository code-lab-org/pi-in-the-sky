
var client = new Paho.MQTT.Client("localhost", 9001, "");

client.connect({
  "onFailure": function(e) {
    console.log(e);
    alert("Error connecting to broker.");
  },
  "onSuccess": function() {
    client.subscribe("time", {
      "onFailure": function(e) {
        console.log(e);
        alert("Error subscribing to topic.");
      }
    });
    client.subscribe("position", {
      "onFailure": function(e) {
        console.log(e);
        alert("Error subscribing to topic.");
      }
    });
    client.subscribe("active_fires", {
      "onFailure": function(e) {
        console.log(e);
        alert("Error subscribing to topic.");
      }
    });
  }
});

client.onMessageArrived = function(message) {
  if(message.destinationName == "time") {
    $("#time").text(message.payloadString);
  }
  if(message.destinationName == "position") {
    $("#position").text(message.payloadString);
  }
  if(message.destinationName == "active_fires") {
    $("#active_fires").text(message.payloadString);
  }
};