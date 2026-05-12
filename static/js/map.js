let map;
let markers = [];
let markerCluster;
let userLatLng = null;
let signalSearchData = [];
let selectedSuggestionIndex = -1;
let currentSearchResults = [];

/* ================= MODERN MARKER ================= */

function getMarkerIcon(status) {

    const colors = {
        "OPEN": "#1565c0",
        "IN_PROGRESS": "#f57c00",
        "RESOLVED": "#2e7d32",
        "REJECTED": "#c62828"
    };

    const color = colors[status] || "#1565c0";

    return L.divIcon({
        className: "",
        html: `
            <div style="
                position:relative;
                width:30px;
                height:30px;
                transform:rotate(-45deg);
            ">
                <div style="
                    width:100%;
                    height:100%;
                    background:${color};
                    border-radius:50% 50% 50% 0;
                    border:3px solid white;
                    box-shadow:
                        0 8px 18px rgba(0,0,0,0.35),
                        0 0 0 3px rgba(255,255,255,0.6);
                "></div>

                <div style="
                    position:absolute;
                    width:10px;
                    height:10px;
                    background:white;
                    border-radius:50%;
                    top:10px;
                    left:10px;
                "></div>
            </div>
        `,
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30]
    });
}

/* ================= CUSTOM TOOLTIP ================= */

const tooltip = document.createElement("div");
tooltip.className = "custom-tooltip";
document.body.appendChild(tooltip);

document.addEventListener("mouseover", function(e){
    const target = e.target.closest("[data-tooltip]");
    if(!target) return;

    tooltip.textContent = target.getAttribute("data-tooltip");
    tooltip.style.opacity = "1";
});

document.addEventListener("mousemove", function(e){
    tooltip.style.left = (e.clientX + 14) + "px";
    tooltip.style.top = (e.clientY + 14) + "px";
});

document.addEventListener("mouseout", function(e){
    if(e.target.closest("[data-tooltip]")){
        tooltip.style.opacity = "0";
    }
});

/* ================= MAP INIT ================= */

function initMap() {

    map = L.map('map').setView([43.214, 27.914], 12);
    const bgBounds = L.latLngBounds(
        [41.2, 22.3],
        [44.3, 28.7]
    );
    map.setMaxBounds(bgBounds);

    map.on('drag', function () {
        map.panInsideBounds(bgBounds, { animate: false });
    });

    map.setMinZoom(7);

    L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',{
        maxZoom: 19,
        attribution:'&copy; OpenStreetMap contributors'
    }).addTo(map);

    /* ================= REGION BOUNDARY ================= */

    fetch(STATIC_URL + "geo/bulgaria_regions.geojson")
    .then(res => res.json())
    .then(data => {

        const varnaFeature = data.features.find(
            f => f.properties.adm1_name1 === "Варна"
        );

        if(!varnaFeature) return;

        L.geoJSON(data,{
            style:function(feature){

                if(feature.properties.adm1_name1 === "Варна"){
                    return {opacity:0,fillOpacity:0};
                }

                return{
                    color:"#c62828",
                    weight:1,
                    fillColor:"#c62828",
                    fillOpacity:0.12
                };
            }
        }).addTo(map);

        const varnaLayer = L.geoJSON(varnaFeature,{
            style:{
                color:"#1565c0",
                weight:3,
                fillOpacity:0,
                opacity:1
            }
        }).addTo(map);

        map.fitBounds(varnaLayer.getBounds());
        map.setZoom(10);

    });

    /* ================= SIGNALS ================= */

    markerCluster = L.markerClusterGroup();
    map.addLayer(markerCluster);

    fetch('/api/map/signals/')
    .then(res => res.json())
    .then(data => {

        const categorySelect = document.getElementById('categorySelect');
        const categories = new Set();
        const bounds = [];

        markers = [];
        signalSearchData = [];

        data.forEach(signal => {

            if(!signal.latitude || !signal.longitude) return;

            const marker = L.marker(
                [
                    parseFloat(signal.latitude),
                    parseFloat(signal.longitude)
                ],
                {
                    icon:getMarkerIcon(signal.status)
                }
            );

            const statusValue = signal.status
                ? signal.status.toLowerCase()
                : "";

            const username = signal.user || "—";

            const formattedDate = signal.created_at
                ? new Date(signal.created_at).toLocaleString('bg-BG')
                : "—";

            marker.bindPopup(`
                <div class="custom-popup">

                    <div class="popup-title">
                        ${signal.title}
                    </div>

                    <div class="popup-row">
                        <span class="popup-label">Категория:</span>
                        <span>${signal.category}</span>
                    </div>

                    <div class="popup-row">
                        <span class="popup-label">Статус:</span>
                        <span class="popup-status status-${statusValue}">
                            ${signal.status_display}
                        </span>
                    </div>

                    <div class="popup-row">
                        <span class="popup-label">Подаден от:</span>
                        <span>${username}</span>
                    </div>

                    <div class="popup-row">
                        <span class="popup-label">Дата:</span>
                        <span>${formattedDate}</span>
                    </div>

                    <div class="popup-actions">

                        <a href="/signals/${signal.id}/"
                           class="popup-btn">
                           Виж детайли
                        </a>

                        ${IS_ADMIN ? `
                            <a href="/signals/${signal.id}/manage/"
                               class="popup-btn popup-admin">
                               ⚙ Управление
                            </a>
                        ` : ``}

                    </div>

                </div>
            `);

            markers.push({
                marker:marker,
                status:signal.status,
                category:signal.category,
                created_at:signal.created_at,
                title:signal.title,
                id:signal.id
            });

            signalSearchData.push({
                id: signal.id,
                title: signal.title || "",
                category: signal.category || "Без категория",
                marker: marker
            });

            categories.add(signal.category);

            bounds.push([
                parseFloat(signal.latitude),
                parseFloat(signal.longitude)
            ]);

        });

        categorySelect.innerHTML = '<option value="ALL">Всички</option>';

        categories.forEach(cat=>{
            const opt = document.createElement('option');
            opt.value = cat;
            opt.textContent = cat;
            categorySelect.appendChild(opt);
        });

        applyFilters();
        document.getElementById("filterResult").innerText =
            "⚲ Показани сигнали: " + markers.length;

        if(bounds.length > 0){
            map.fitBounds(bounds,{padding:[200,200]});
        }
        setupSignalSearch();

    });

    const filterInputs = [
        'statusSelect',
        'categorySelect',
        'dateFrom',
        'dateTo'
    ];

    filterInputs.forEach(id => {
        document.getElementById(id).addEventListener('change', applyFilters);
    });



}

function setupSignalSearch(){

    const input = document.getElementById("signalSearchInput");
    const suggestions = document.getElementById("signalSuggestions");

    if(!input || !suggestions) return;

    const hideSuggestions = () => {
        suggestions.classList.remove("show");
        suggestions.innerHTML = "";
        selectedSuggestionIndex = -1;
    };

    const renderSuggestions = (results) => {
        suggestions.innerHTML = "";
        selectedSuggestionIndex = -1;
        currentSearchResults = results;

        if(!results.length){
            hideSuggestions();
            return;
        }

        results.forEach((signal, index) => {
            const li = document.createElement("li");
            li.className = "search-suggestion-item";
            li.setAttribute("role", "option");
            li.dataset.index = String(index);
            li.innerHTML = `
                ${signal.title}
                <span class="search-suggestion-meta">${signal.category}</span>
            `;

            li.addEventListener("click", () => openSignalDetails(signal));
            suggestions.appendChild(li);
        });

        suggestions.classList.add("show");
    };

    input.addEventListener("input", function(){
        const query = this.value.trim().toLowerCase();

        if(!query){
            currentSearchResults = [];
            hideSuggestions();
            return;
        }

        const results = signalSearchData
            .filter(item => item.title.toLowerCase().includes(query))
            .slice(0, 8);

        renderSuggestions(results);
    });

    input.addEventListener("keydown", function(event){
        const items = Array.from(suggestions.querySelectorAll(".search-suggestion-item"));
        if(!items.length) return;

        if(event.key === "ArrowDown"){
            event.preventDefault();
            selectedSuggestionIndex = (selectedSuggestionIndex + 1) % items.length;
            updateActiveSuggestion(items);
        } else if(event.key === "ArrowUp"){
            event.preventDefault();
            selectedSuggestionIndex = (selectedSuggestionIndex - 1 + items.length) % items.length;
            updateActiveSuggestion(items);
        } else if(event.key === "Enter"){
            event.preventDefault();
            const index = selectedSuggestionIndex >= 0 ? selectedSuggestionIndex : 0;
            const signal = currentSearchResults[index];
            if(signal) openSignalDetails(signal);
        } else if(event.key === "Escape"){
            hideSuggestions();
        }
    });

    document.addEventListener("click", function(event){
        if(!event.target.closest("#mapSearch")){
            hideSuggestions();
        }
    });
}

function updateActiveSuggestion(items){
    items.forEach((item, idx) => {
        item.classList.toggle("active", idx === selectedSuggestionIndex);
    });
}

function openSignalDetails(signal){
    if(signal.marker){
        markerCluster.zoomToShowLayer(signal.marker, function(){
            map.setView(signal.marker.getLatLng(), Math.max(map.getZoom(), 15), { animate: true });
            signal.marker.openPopup();
        });
    }

    window.location.href = `/signals/${signal.id}/`;
}

/* ================= FILTERS ================= */

function applyFilters(){

    let visibleCount = 0;

    const status = document.getElementById('statusSelect').value;
    const category = document.getElementById('categorySelect').value;
    const dateFrom = document.getElementById('dateFrom').value;
    const dateTo = document.getElementById('dateTo').value;
    const errorDiv = document.getElementById('dateError');
    const distanceRange = document.getElementById("distanceRange");
    const distance = distanceRange ? distanceRange.value : null;

    if(dateFrom && dateTo && dateFrom > dateTo){
        errorDiv.style.display="block";
        return;
    }else{
        errorDiv.style.display="none";
    }

    markerCluster.clearLayers();

    markers.forEach(item=>{

        if(status !== "ALL" && item.status !== status){
            return;
        }

        if(category !== "ALL" && item.category !== category){
            return;
        }

        const itemDate = item.created_at
            ? item.created_at.substring(0,10)
            : null;

        if(dateFrom && itemDate && itemDate < dateFrom){
            return;
        }

        if(dateTo && itemDate && itemDate > dateTo){
            return;
        }

        // ================= DISTANCE FILTER =================
        if(userLatLng && distance && !isNaN(distance)){

            const from = turf.point([userLatLng[1], userLatLng[0]]);
            const to = turf.point([
                item.marker.getLatLng().lng,
                item.marker.getLatLng().lat
            ]);

            const dist = turf.distance(from, to, { units: 'kilometers' });

            if(dist > distance){
                return;
            }
        }

        markerCluster.addLayer(item.marker);
        visibleCount++;

    });
    document.getElementById("filterResult").innerText =
        "⚲ Показани сигнали: " + visibleCount;
}

/* ================= FILTER PANEL ================= */

function toggleFilter(){
    document.getElementById("filterPanel")
        .classList.toggle("show");
}

    document.addEventListener("DOMContentLoaded",initMap);
    document.addEventListener("DOMContentLoaded", function(){
        loadWeather();

        setInterval(loadWeather, 600000);
    });

document.addEventListener("DOMContentLoaded", function(){

    const distanceRange = document.getElementById("distanceRange");
    const distanceValue = document.getElementById("distanceValue");

    if(distanceRange){
        distanceRange.addEventListener("input", function(){

            distanceValue.textContent = this.value + " км";

            if(userLocationCircle){
                userLocationCircle.setRadius(this.value * 1000);
            }

            applyFilters();
        });
    }

});

/* ================= USER LOCATION ================= */

let userLocationMarker=null;
let userLocationCircle=null;

function showUserLocation(){

    if(!navigator.geolocation){
        alert("Браузърът не поддържа геолокация.");
        return;
    }

    map.getContainer().style.cursor="wait";

    navigator.geolocation.getCurrentPosition(function(position){

        const latlng = [
            position.coords.latitude,
            position.coords.longitude
        ];

        // ✅ SAVE USER LOCATION
        userLatLng = latlng;

        // ✅ UNLOCK SLIDER
        document.getElementById("distanceRange").disabled = false;
        document.getElementById("getLocationBtn").textContent = "Локацията е намерена";

        if(userLocationMarker){
            map.removeLayer(userLocationMarker);
            map.removeLayer(userLocationCircle);
        }

        userLocationMarker = L.circleMarker(latlng,{
            radius:10,
            fillColor:"#1e88e5",
            color:"#ffffff",
            weight:4,
            opacity:1,
            fillOpacity:1
        }).addTo(map);

        userLocationCircle = L.circle(latlng,{
            radius:position.coords.accuracy,
            color:"#1e88e5",
            weight:1,
            fillOpacity:0.15
        }).addTo(map);

        map.setView(latlng,16);
        userLocationMarker.bringToFront();

        map.getContainer().style.cursor="default";
        applyFilters();

    },function(){

        alert("Не успяхме да получим вашата локация.");

        map.getContainer().style.cursor="default";

    });

}

function resetFilters(){

    // стандартни филтри
    document.getElementById('statusSelect').value = "ALL";
    document.getElementById('categorySelect').value = "ALL";
    document.getElementById('dateFrom').value = "";
    document.getElementById('dateTo').value = "";

    // ================= NEW (distance reset) =================

    const distanceRange = document.getElementById("distanceRange");
    const distanceValue = document.getElementById("distanceValue");

    if(distanceRange){
        distanceRange.value = 5;
        distanceRange.disabled = true;
    }

    if(distanceValue){
        distanceValue.textContent = "5 км";
    }

    // махаме user location
    userLatLng = null;

    // махаме marker и circle
    if(userLocationMarker){
        map.removeLayer(userLocationMarker);
        userLocationMarker = null;
    }

    if(userLocationCircle){
        map.removeLayer(userLocationCircle);
        userLocationCircle = null;
    }

    // връщаме текста на бутона
    const btn = document.getElementById("getLocationBtn");
    if(btn){
        btn.textContent = "⚲ Намери локация";
    }

    // apply filters отново
    applyFilters();
}

/* ================= WEATHER ================= */

function loadWeather(){

    const tempEl = document.querySelector(".weather-temp");
    const iconEl = document.querySelector(".weather-icon");
    const descEl = document.querySelector(".weather-desc");

    if(!tempEl || !iconEl || !descEl) return;

    fetch("https://api.open-meteo.com/v1/forecast?latitude=43.2079&longitude=27.9156&current_weather=true")
    .then(res => res.json())
    .then(data => {

        const temp = Math.round(data.current_weather.temperature);
        const code = data.current_weather.weathercode;

        tempEl.innerText = temp + "°C";

        let icon = "☀️";
        let description = "Ясно";

        // ☁️ облаци
        if(code >= 1 && code <= 3){
            icon = "⛅";
            description = "Разкъсана\nоблачност";
        }

        // 🌫 мъгла
        else if(code >= 45 && code <= 48){
            icon = "😶‍🌫️";
            description = "Мъгла";
        }

        // 🌧 дъжд
        else if(code >= 51 && code <= 67){
            icon = "🌧️";
            description = "Дъжд";
        }

        // ❄ сняг
        else if(code >= 71 && code <= 77){
            icon = "❄️";
            description = "Сняг";
        }

        // 🌦 превалявания
        else if(code >= 80 && code <= 99){
            icon = "⛈️";
            description = "Превалявания";
        }

        iconEl.innerText = icon;
        descEl.innerText = description;

    })
    .catch(err => {
        console.log("Weather error:", err);
    });
}