// scripts.js

var map = L.map('map', {
    worldCopyJump: false, continuousWorld: false
}).setView([54.5260, 15.2551], 4); // Center on Europe

L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
}).addTo(map);

var currentMarker = null;

function onMapClick(e) {
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

function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

map.on('click', onMapClick);

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
        html += `<div class="info-section"><h3>Nearest Urban Center</h3><p>${data.nearest_urban_center.name} (${data.nearest_urban_center.latitude}, ${data.nearest_urban_center.longitude})</p></div>`;
    }

    return html;
}

function renderWeatherInfo(data) {
    let html = '';

    if (data.current_weather) {
        html += `<div class="info-section"><h3>Current Weather</h3>`;
        html += `<div class="weather-item"><p><strong>Cloud Cover:</strong> ${data.current_weather.cloud_cover}%</p></div>`;

        html += `<div class="weather-item"><p><strong>Time of Day:</strong> ${data.current_weather.is_day ? 'Day' : 'Night'}</p></div>`;
        html += `<div class="weather-item"><p><strong>Precipitation:</strong> ${data.current_weather.precipitation} mm</p></div>`;
        html += `<div class="weather-item"><p><strong>Temperature:</strong> ${data.current_weather.temperature_2m.toFixed(2)} °C</p></div>`;
        html += `<div class="weather-item"><p><strong>Time:</strong> ${new Date(data.current_weather.time * 1000).toLocaleString()}</p></div>`;
        html += `</div>`;
    }

    if (data.hourly_weather) {
        html += `<div class="info-section"><h3>Hourly Weather</h3>`;
        data.hourly_weather.forEach(hour => {
            html += `<p>${new Date(hour.date).toLocaleString()}: ${hour.temperature_2m}°C, Precipitation: ${hour.precipitation}mm, Cloud Cover: ${hour.cloud_cover}%</p>`;
        });
        html += `</div>`;
    }

    if (data.daily_weather) {
        html += `<div class="info-section"><h3>Daily Weather</h3>`;
        data.daily_weather.forEach(day => {
            html += `<p>${new Date(day.date).toLocaleDateString()}: Precipitation Probability: ${day.precipitation_probability_max}%</p>`;
        });
        html += `</div>`;
    }

    return html;
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

