// scripts.js

var map = L.map('map', {
    worldCopyJump: false,
    continuousWorld: false,
    zoomControl: false
}).setView([54.5260, 15.2551], 4); // Center on Europe

L.control.zoom({
    position: 'bottomleft'
}).addTo(map);

L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
}).addTo(map);

var currentMarker = null;

const sidebar = document.querySelector('.sidebar');
const resizer = document.querySelector('.resizer');

let isResizing = false;

resizer.addEventListener('mousedown', function(e) {
    isResizing = true;
    document.body.style.cursor = 'ew-resize';  // Change cursor to resizing mode
});

// Mouse move event to dynamically resize the sidebar
document.addEventListener('mousemove', function(e) {
    if (isResizing) {
        // Calculate the new width for the sidebar based on the mouse position
        const newWidth = window.innerWidth - e.clientX;

        // Apply the new width to the sidebar (limit the width to avoid overlap)
        if (newWidth > 200 && newWidth < 600) {
            sidebar.style.width = `${newWidth}px`;
            resizer.style.left = `${window.innerWidth - newWidth -25}px`;
            map.style.marginRight = `${newWidth}px`;
        }
    }
});

// Mouse up event to stop resizing
document.addEventListener('mouseup', function() {
    if (isResizing) {
        isResizing = false;
        document.body.style.cursor = '';
    }
});


function onMapClick(e) {
    console.log("Map clicked!");
    var lat = e.latlng.lat;
    var lon = e.latlng.lng;

    if (currentMarker) {
        map.removeLayer(currentMarker);
    }

    currentMarker = L.marker([lat, lon]).addTo(map);

    console.log(`Clicked on Latitude: ${lat}, Longitude: ${lon}`);  // Debugging info

    $.ajax({
        url: '/process_coordinates',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({latitude: lat, longitude: lon}),
        success: function (response) {
            console.log('Response received:', response);  // Debugging info

            if (response.data) {
                $('#Geographical').html(renderGeographicalInfo(response.data));
                $('#Weather').html(renderWeatherInfo(response.data));
                $('#Astronomical').html(renderAstronomicalInfo(response.data));
            } else {
                console.log('No data found in the response');  // Debugging info
            }
        },
        error: function (xhr, status, error) {
            console.error('Error occurred:', error);
            $('#Geographical').html(`<div>Error: ${xhr.responseJSON.error}</div>`);
        }
    });
}

map.on('click', onMapClick);

function openTab(evt, tabName) {
    var i, tabcontent;
    tabcontent = document.getElementsByClassName("tabcontent");

    // Hide all tab content sections
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Show the selected tab content
    document.getElementById(tabName).style.display = "block";
}


function renderGeographicalInfo(data) {
    let html = '';

    if (data.terrain_types) {
        html += `<div class="info-section"><h3>Terrain Types</h3><p>${data.terrain_types}</p></div>`;
    }

    if (data.elevation) {
        html += `<div class="info-section"><h3>Elevation</h3><p>${data.elevation} meters</p></div>`;
    }

    if (data.location_info) {
        html += `<div class="info-section"><h3>Location Info</h3>`;
        Object.entries(data.location_info).forEach(([key, value]) => {
            // Round latitude and longitude to 4 decimal places
            if (key.toLowerCase() === 'latitude' || key.toLowerCase() === 'longitude') {
                value = parseFloat(value).toFixed(4);
            }
            html += `<p>${key.replace(/_/g, ' ').toUpperCase()}: ${value}</p>`;
        });
        html += `</div>`;
    }

    if (data.urban_centers) {
        html += `<div class="info-section"><h3>Urban Centers</h3>`;
        data.urban_centers.forEach(center => {
            html += `<p>${center.name} (${Number(center.latitude.toFixed(2))}, ${Number(center.longitude.toFixed(2))}) ${center.distance.toFixed(2)} km away</p>`;
        });
        html += `</div>`;
    }

    if (data.distance_from_urban_center) {
        html += `<div class="info-section"><h3>Distance from Nearest Urban Center</h3><p>${data.distance_from_urban_center.toFixed(2)} km</p></div>`;
    }

    if (data.nearest_urban_center) {
        html += `<div class="info-section"><h3>Nearest Urban Center</h3><p>${data.nearest_urban_center.name} (${data.nearest_urban_center.latitude.toFixed(2)}, ${data.nearest_urban_center.longitude.toFixed(2)})</p></div>`;
    }

    return html;
}


function renderWeatherInfo(data) {
    // Extract hourly data
    const hours = data.hourly_weather.map(hour => new Date(hour.date).toLocaleTimeString());
    const temperatures = data.hourly_weather.map(hour => hour.temperature_2m);
    const cloudCover = data.hourly_weather.map(hour => hour.cloud_cover);
    const precipitation = data.hourly_weather.map(hour => hour.precipitation);
    const cloudCoverEmojis = data.hourly_weather.map(hour => hour.cloud_cover_emoji);

    createLineChart('temperatureChart', 'Temperature (°C)', hours, temperatures, 'rgba(255, 99, 132, 0.6)', 'Temperature');
    createLineChartWithEmojis('cloudCoverChart', 'Cloud Cover (%)', hours, cloudCover, cloudCoverEmojis, 'rgba(54, 162, 235, 0.6)', 'Cloud Cover');
    createBarChart('precipitationChart', 'Precipitation (mm)', hours, precipitation, 'rgba(75, 192, 192, 0.6)', 'Precipitation');
}

// keeping track of the charts
let temperatureChart = null;
let cloudCoverChart = null;
let precipitationChart = null;

function createLineChart(canvasId, label, labels, data, backgroundColor, datasetLabel) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    // Destroy the previous chart if it exists
    if (temperatureChart) {
        temperatureChart.destroy();
    }

    temperatureChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: datasetLabel,
                data: data,
                backgroundColor: backgroundColor,
                borderColor: backgroundColor,
                borderWidth: 2,
                fill: false
            }]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Time' },
                    ticks: { maxRotation: 45, minRotation: 45 }
                },
                y: {
                    title: { display: true, text: label }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        boxWidth: 20
                    }
                }
            }
        }
    });
}

function createLineChartWithEmojis(canvasId, label, labels, data, emojiLabels, backgroundColor, datasetLabel) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    // deleting the previous chart
    if (cloudCoverChart) {
        cloudCoverChart.destroy();
    }

    cloudCoverChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels.map((time, index) => time + ' ' + emojiLabels[index]), // Add emojis to labels
            datasets: [{
                label: datasetLabel,
                data: data,
                backgroundColor: backgroundColor,
                borderColor: backgroundColor,
                borderWidth: 2,
                fill: false
            }]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Time' },
                    ticks: { maxRotation: 45, minRotation: 45 }
                },
                y: {
                    title: { display: true, text: label }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        boxWidth: 20
                    }
                }
            }
        }
    });
}

function createBarChart(canvasId, label, labels, data, backgroundColor, datasetLabel) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    // deleting the previous chart
    if (precipitationChart) {
        precipitationChart.destroy();
    }

    precipitationChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: datasetLabel,
                data: data,
                backgroundColor: backgroundColor,
                borderColor: backgroundColor,
                borderWidth: 2
            }]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Time' },
                    ticks: { maxRotation: 45, minRotation: 45 }
                },
                y: {
                    title: { display: true, text: label }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        boxWidth: 20
                    }
                }
            }
        }
    });
}


function renderAstronomicalInfo(data) {
    let html = '';

    if (data.astronomical_events) {
        html += `<div class="info-section"><h3>Astronomical Events</h3>`;

        if (data.astronomical_events.visible_planets) {
            html += `<h4>Visible Planets</h4>`;
            data.astronomical_events.visible_planets.forEach(event => {
                html += `<p>${event.planet} at ${new Date(event.time).toLocaleTimeString()}: Altitude ${event.altitude.toFixed(2)}, Azimuth ${event.azimuth.toFixed(2)}</p>`;
            });
        }

        if (data.astronomical_events.conjunctions) {
            html += `<h4>Conjunctions</h4>`;
            data.astronomical_events.conjunctions.forEach(event => {
                html += `<p>${event.description} at ${new Date(event.time).toLocaleTimeString()}</p>`;
            });
        }

        if (data.astronomical_events.meteor_showers) {
            html += `<h4>Meteor Showers</h4>`;
            data.astronomical_events.meteor_showers.forEach(event => {
                html += `<p>${event.name} peak at ${new Date(event.peak).toLocaleDateString()}</p>`;
            });
        }

        if (data.astronomical_events.moon_info) {
            html += `<h4>Moon Info</h4>`;
            html += `<p>Moonrise: ${new Date(data.astronomical_events.moon_info.moonrise).toLocaleTimeString()}</p>`;
            html += `<p>Moonset: ${new Date(data.astronomical_events.moon_info.moonset).toLocaleTimeString()}</p>`;
            html += `<p>Moon Phase: ${data.astronomical_events.moon_info.moon_phase ? data.astronomical_events.moon_info.moon_phase : 'Unknown'}</p>`;
        }

        html += `</div>`;
    }

    return html;
}

