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
  }
});

client.onMessageArrived = function(message) {
  if(message.destinationName == "time") {
    $("#time").text(message.payloadString);
  }
};
