// ThingSpeak API
const readAPIUrl = "https://api.thingspeak.com/channels/3014763/feeds.json?api_key=F7KC5BG7SFPDMUNZ&results=4";

let intervalId = null;

// Chart data
let tempData = [];
let humidityData = [];
let labels = [];

// Charts
var tempChart = new ApexCharts(document.querySelector("#temperature-chart"), {
  chart: { type: 'line', height: 350 },
  series: [{ name: 'Temperature', data: [] }],
  xaxis: { categories: [] }
});
tempChart.render();

var humidityChart = new ApexCharts(document.querySelector("#humidity-chart"), {
  chart: { type: 'line', height: 350 },
  series: [{ name: 'Humidity', data: [] }],
  xaxis: { categories: [] }
});
humidityChart.render();


// Fetch data
function fetchThingSpeakData() {
  fetch(readAPIUrl)
    .then(res => res.json())
    .then(data => {
      if (data.feeds.length > 0) {

        const d = data.feeds[0];

        let temp = d.field1 ? parseFloat(d.field1).toFixed(2) : "N/A";
        let hum = d.field2 ? parseFloat(d.field2).toFixed(2) : "N/A";
        let moist = d.field3 ? parseFloat(d.field3).toFixed(2) : "N/A";
        let fan = d.field4 ? (d.field4 === "1" ? "ON" : "OFF") : "N/A";
        let attack = d.field5 ? parseInt(d.field5) : 0;

        // Update cards
        document.querySelector(".card:nth-child(1) .font-weight-bold").innerText = temp + " °C";
        document.querySelector(".card:nth-child(2) .font-weight-bold").innerText = hum + " %";
        document.querySelector(".card:nth-child(3) .font-weight-bold").innerText = moist;
        document.querySelector(".card:nth-child(4) .font-weight-bold").innerText = fan;

        // ALERT SYSTEM
        const alertBox = document.getElementById("alert-box");

        if (attack === 1) {
          alertBox.innerText = "🚨 Attack detected and blocked";
          alertBox.style.color = "red";
        } else {
          alertBox.innerText = "✅ System Secure";
          alertBox.style.color = "green";
        }

        // Update charts
        if (temp !== "N/A" && hum !== "N/A") {

          if (tempData.length >= 10) {
            tempData.shift();
            humidityData.shift();
            labels.shift();
          }

          let time = new Date().toLocaleTimeString();

          tempData.push(parseFloat(temp));
          humidityData.push(parseFloat(hum));
          labels.push(time);

          tempChart.updateOptions({ xaxis: { categories: labels } });
          tempChart.updateSeries([{ data: tempData }]);

          humidityChart.updateOptions({ xaxis: { categories: labels } });
          humidityChart.updateSeries([{ data: humidityData }]);
        }
      }
    })
    .catch(err => console.error(err));
}


// BUTTON FUNCTIONS

function showData() {
  if (intervalId) return;

  fetchThingSpeakData();
  intervalId = setInterval(fetchThingSpeakData, 5000);
}

function hideData() {
  clearInterval(intervalId);
  intervalId = null;

  // Reset values
  document.querySelector(".card:nth-child(1) .font-weight-bold").innerText = "N/A";
  document.querySelector(".card:nth-child(2) .font-weight-bold").innerText = "N/A";
  document.querySelector(".card:nth-child(3) .font-weight-bold").innerText = "N/A";
  document.querySelector(".card:nth-child(4) .font-weight-bold").innerText = "N/A";

  document.getElementById("alert-box").innerText = "N/A";

  // Reset charts
  tempData = [];
  humidityData = [];
  labels = [];

  tempChart.updateSeries([{ data: [] }]);
  humidityChart.updateSeries([{ data: [] }]);
}