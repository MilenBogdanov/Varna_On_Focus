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

        if(code === 0){
            icon = "☀️";
            description = "Ясно";
        }
        else if(code >= 1 && code <= 3){
            icon = "⛅";
            description = "Разкъсана\nоблачност";
        }
        else if(code >= 45 && code <= 48){
            icon = "😶‍🌫️";
            description = "Мъгла";
        }
        else if(code >= 51 && code <= 67){
            icon = "🌧️";
            description = "Дъжд";
        }
        else if(code >= 71 && code <= 77){
            icon = "❄️";
            description = "Сняг";
        }
        else if(code >= 80 && code <= 99){
            icon = "⛈️";
            description = "Превалявания";
        }

        iconEl.innerText = icon;
        descEl.innerText = description;

    })
    .catch(err => console.log("Weather error:", err));
}

/* ================= INIT ================= */

document.addEventListener("DOMContentLoaded", function(){

    loadWeather();

    // обновяване на всеки 10 мин
    setInterval(loadWeather, 600000);

});