// Initialize Socket.IO connection with proper configuration
let socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port, {
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  reconnectionAttempts: 5,
  transports: ['websocket', 'polling']
});

// Global variables
let g;
let path;
let legendGroup;
let projection;
let wildfireData = [];
let weatherData = [];
let fips2County = {}


// Create a completely new tooltip function
function showTooltip(message, x, y) {
    // Remove any existing tooltip first
    d3.selectAll(".tooltip-test").remove();
    
    // Create a new tooltip div directly
    const tooltipDiv = document.createElement("div");
    tooltipDiv.className = "tooltip-test";
    tooltipDiv.innerHTML = message;
    tooltipDiv.style.position = "absolute";
    tooltipDiv.style.left = (x + 10) + "px";
    tooltipDiv.style.top = (y - 28) + "px";
    tooltipDiv.style.backgroundColor = "white";
    tooltipDiv.style.padding = "10px";
    tooltipDiv.style.border = "1px solid #ddd";
    tooltipDiv.style.borderRadius = "4px";
    tooltipDiv.style.pointerEvents = "none";
    tooltipDiv.style.zIndex = "1000";
    tooltipDiv.style.boxShadow = "0 2px 4px rgba(0,0,0,0.1)";
    
    // Add to body
    document.body.appendChild(tooltipDiv);

}

function hideTooltip() {
    const tooltips = document.querySelectorAll(".tooltip-test");
    tooltips.forEach(el => el.remove());
}

// Add CSS styles for tooltip (with !important)
const tooltipStyles = document.createElement('style');
tooltipStyles.textContent = `
    .tooltip-test {
        position: absolute !important;
        background: white !important;
        padding: 10px !important;
        border: 1px solid #ddd !important;
        border-radius: 4px !important;
        pointer-events: none !important;
        z-index: 1000 !important;
        font-size: 12px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
`;
document.head.appendChild(tooltipStyles);

function formatValue(value, type) {
    if (value === undefined || value === null) return 'N/A';
    
    switch(type) {
        case 'temperature':
            return `${(value * 9/5 + 32).toFixed(1)}°F`
        case 'precipitation':
            return `${value.toFixed(2)} inches`;
        case 'wind':
            return `${(value * 2.23694).toFixed(1)} mph`;
        case 'fuel':
            return `${value.toFixed(1)} tons/acre`;
        default:
            return value.toString();
    }
}

function getDataTypeLabel(selectedMapType) {
    switch(selectedMapType) {
        case 'temperature-checkbox':
            return 'Temperature';
        case 'rain-checkbox':
            return 'Precipitation';
        case 'wind-checkbox':
            return 'Wind Speed';
        case 'fuel-checkbox':
            return 'Fuel Moisture';
        default:
            return '';
    }
}

// Color scales
const wildfireColorScale = d3.scaleThreshold()
    .domain([0.25, 10, 100, 300, 1000])
    .range(['#fee5d9', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15', '#67000d']);

const temperatureScale = d3.scaleThreshold()
    .domain([32.00, 47.75, 63.50, 79.25])
    .range(['#f2f0f7', '#cbc9e2', '#9e9ac8', '#756bb1', '#54278f']);

const precipitationScale = d3.scaleThreshold()
    .domain([0.98, 1.97, 2.95, 3.94])
    .range(['#deebf7', '#9ecae1', '#4292c6', '#08519c']);

const windScale = d3.scaleThreshold()
    .domain([6, 12, 18, 24])
    .range(['#f0f9f8', '#bae4e3', '#67c6c4', '#2a9c9b', '#00ffff']);

const fuelColorScale = d3.scaleQuantile()
    .domain([0, 50, 100, 150, 200])
    .range(['#f7fcb9', '#addd8e', '#78c679', '#31a354', '#006837']);

// Define wildfire size to radius mapping
const wildFireRadii = [
    [0, 0],     // 0-0.25 acres -> 0.25px radius
    [0.25, 3],     // 0.25-10 acres -> 3px radius
    [10, 5],       // 10-100 acres -> 5px radius
    [100, 7],      // 100-300 acres -> 7px radius
    [300, 9],      // 300-1000 acres -> 9px radius
    [1000, 11]     // >= 1000 acres -> 11px radius
];

function getWildfireRadius(fireSize) {
    // If size is less than 0.25, return 0
    if (fireSize < 0.25) return 0;
    
    // Otherwise, return the appropriate radius based on the fire size
    for (let i = wildFireRadii.length - 1; i >= 0; i--) {
        let [area, radius] = wildFireRadii[i];
        if (fireSize >= area) return radius;
    }
    return 0; // default smallest radius
}

function requestDataBody(date) {
    const requestDate = new Date(date);
    requestDate.setHours(12, 0, 0, 0);
    
    return {
        time: requestDate.getTime() / 1000
    };
}

// Initialize visualization when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Load required data to draw the map
    Promise.all([
        d3.json("/static/us-counties.json"),
        d3.csv("/static/county_fips.csv")
    ]).then(startVisualization)
    .catch(error => {
        console.error("Error loading data:", error);
    });
});

function startVisualization([us, fips]) {
    try {
        // Convert the read csv to a lookup table to map FIPS to county name
        fips.forEach((item) => {
            fips2County[item["fips"]] = item["county_name"];
        })

        // Set up the SVG
        const width = 960;
        const height = 600;
        const svg = d3.select("#wildfire-map")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", `0 0 ${width} ${height}`)
            .style("width", "100%")
            .style("height", "auto");

        // Set up the projection
        projection = d3.geoAlbersUsa()
            .scale(1000)
            .translate([width / 2, height / 2]);

        path = d3.geoPath().projection(projection);

        // Create main group for the map
        g = svg.append("g");

        // Create legend group
        legendGroup = svg.append("g")
            .attr("class", "legend-group")
            .attr("transform", "translate(50, 50)");

        // Draw counties
        const counties = topojson.feature(us, us.objects.counties);
        const countyPaths = g.selectAll("path.county")
            .data(counties.features)
            .enter()
            .append("path")
            .attr("class", "county")
            .attr("d", path)
            .attr("fill", "rgb(194,194,194)")
            .attr("stroke", "#333")
            .attr("stroke-width", 0.3);
            
        // Add event listeners separately
        countyPaths.on("mouseover", function(event, d) {
            const selectedMapType = document.querySelector('input[name="map-type"]:checked').id;
            let additionalInfo = '';
            
            // Find weather data for this county
            const countyWeather = wildfireData.find(w => w.fips === event.id);
            const countyWildfire = wildfireData.find(w => w.fips === event.id);
            
            if (countyWeather) {
                switch(selectedMapType) {
                    case 'temperature-checkbox':
                        if (countyWeather.tmax !== undefined) {
                            additionalInfo = `<br>Temperature: ${formatValue(countyWeather.tmax, 'temperature')}`;
                        }
                        break;
                    case 'rain-checkbox':
                        if (countyWeather.prcp !== undefined) {
                            additionalInfo = `<br>Precipitation: ${formatValue(countyWeather.prcp, 'precipitation')}`;
                        }
                        break;
                    case 'wind-checkbox':
                        if (countyWeather.wind_speed !== undefined) {
                            additionalInfo = `<br>Wind Speed: ${formatValue(countyWeather.wind_speed, 'wind')}`;
                        }
                        break;
                    case 'fuel-checkbox':
                        if (countyWeather.fmc !== undefined) {
                            additionalInfo = `<br>Fuel Moisture: ${formatValue(countyWeather.fmc, 'fuel')}`;
                        }
                        break;
                }
            }
    
            const tooltipContent = `<strong>Details</strong><br>` +
                `Location: ${fips2County[event.id] || 'Unknown County'}` +
                (countyWildfire ? `<br>Wildfire Size: ${countyWildfire.fire_size} acres` : '<br>No wildfires') +
                additionalInfo;

            const mouseX = event?.pageX || (d3.event?.pageX) || 0;
            const mouseY = event?.pageY || (d3.event?.pageY) || 0;
            showTooltip(tooltipContent, mouseX, mouseY);
        });
        
        countyPaths.on("mousemove", function(event) {
            const mouseX = event?.pageX || (d3.event?.pageX) || 0;
            const mouseY = event?.pageY || (d3.event?.pageY) || 0;
            
            // Update tooltip position
            const tooltips = document.querySelectorAll(".tooltip-test");
            tooltips.forEach(tooltip => {
                tooltip.style.left = (mouseX + 10) + "px";
                tooltip.style.top = (mouseY - 28) + "px";
            });
        });
        
        countyPaths.on("mouseout", function() {
            hideTooltip();
        });

        // Draw state borders
        g.append("path")
            .datum(topojson.mesh(us, us.objects.states, (a, b) => a !== b))
            .attr("class", "state-borders")
            .attr("d", path)
            .attr("fill", "none")
            .attr("stroke", "#000")
            .attr("stroke-width", 0.6);

        // Initialize controls after map is drawn
        initializeControls();

    } catch (error) {
        console.error("Error in startVisualization:", error);
    }
}

function initializeControls() {
    try {
        // Initialize wildfire checkbox
        const wildfireCheckbox = document.getElementById('wildfire-checkbox');
        wildfireCheckbox.addEventListener('change', redrawMap);
        // Initialize radio buttons
        const radioButtons = document.querySelectorAll('input[name="map-type"]');
        radioButtons.forEach(radio => {
            radio.addEventListener('change', redrawMap);
        });

        // Initialize date controls
        const datePicker = document.getElementById('datePicker');
        const dateSlider = document.getElementById('dateSlider');
        const dateDisplay = document.getElementById('date-display');

        if (!datePicker || !dateSlider || !dateDisplay) {
            console.error("Date control elements not found:", {
                datePicker: !!datePicker,
                dateSlider: !!dateSlider,
                dateDisplay: !!dateDisplay
            });
            return;
        }

        // Set date picker range
        const today = new Date();
        const maxDate = new Date(today);
        maxDate.setDate(today.getDate() + 14);
        const minDate = new Date("1992-01-01");
        
        datePicker.min = minDate.toISOString().split('T')[0];
        datePicker.max = maxDate.toISOString().split('T')[0];
        datePicker.value = maxDate.toISOString().split('T')[0];

        // Configure date slider
        const totalDays = Math.ceil((maxDate - minDate) / (1000 * 60 * 60 * 24));
        dateSlider.min = 0;
        dateSlider.max = totalDays;
        dateSlider.value = totalDays; // Start at max date

        // Function to update display and request data
        function updateDateDisplay(date) {
            dateDisplay.textContent = `Date selected: ${date.toLocaleDateString('en-US', { 
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            })}`;
            socket.emit('data_request', requestDataBody(date));
        }

        // Update picker when slider changes
        dateSlider.addEventListener('input', (event) => {
            const days = parseInt(event.target.value);
            const selectedDate = new Date(minDate);
            selectedDate.setDate(minDate.getDate() + days);
            selectedDate.setHours(12, 0, 0, 0); // Set to noon
            datePicker.value = selectedDate.toISOString().split('T')[0];
            updateDateDisplay(selectedDate);
        });

        // Update slider when picker changes
        datePicker.addEventListener('change', (event) => {
            const selectedDate = new Date(event.target.value + 'T12:00:00');
            const days = Math.floor((selectedDate - minDate) / (1000 * 60 * 60 * 24));
            dateSlider.value = days;
            updateDateDisplay(selectedDate);
        });

        // Initialize with current date
        datePicker.dispatchEvent(new Event('change'));
    } catch (error) {
        console.error("Error in initializeControls:", error);
    }
}

function redrawMap() {
    // Clear existing markers efficiently
    g.selectAll(".weather-marker, .wildfire-marker, .temperature-marker").remove();

    const selectedMapType = document.querySelector('input[name="map-type"]:checked').id;

    // Update county colors
    g.selectAll(".county")
        .transition()
        .duration(100) // Reduced transition time
        .attr("fill", d => getCountyColor(d, selectedMapType));

    // Add wildfire markers if checkbox is checked
    if (document.getElementById('wildfire-checkbox').checked) {
        drawWildfireMarkers();
    }

    // Update legend
    updateLegend(selectedMapType);
}

function getCountyColor(d, selectedMapType) {
    const fips = d.id;
    
    d.weatherData = wildfireData.find(w => w.fips === fips);

    switch(selectedMapType) {
        case 'temperature-checkbox':
            return d.weatherData?.tmax ? temperatureScale(d.weatherData.tmax) : 'rgb(194,194,194)';
        
        case 'rain-checkbox':
            // Check if we have precipitation data for this county
            if (d.weatherData && d.weatherData.prcp !== undefined) {
                // Make sure it's a number
                let prcp = typeof d.weatherData.prcp === 'string' ? 
                    parseFloat(d.weatherData.prcp) : d.weatherData.prcp;
                
                // Use precipitation scale for this county
                return precipitationScale(prcp);
            }
            return 'rgb(194,194,194)';
        
        case 'wind-checkbox':
            return d.weatherData?.wind_speed ? windScale(d.weatherData.wind_speed) : 'rgb(194,194,194)';
        
        case 'fuel-checkbox':
            return d.weatherData?.fmc ? fuelColorScale(d.weatherData.fmc) : 'rgb(194,194,194)';
        
        default:
            return 'rgb(194,194,194)';
    }
}

function drawWildfireMarkers() {
    // Filter out invalid coordinates and those outside US bounds
    const validData = wildfireData.filter(d => {
        // Check if coordinates are within US bounds
        if (d.LATITUDE < 24.0 || d.LATITUDE > 50.0 || 
            d.LONGITUDE < -125.0 || d.LONGITUDE > -66.0) {
            return false;
        }
        
        // Pre-calculate projection
        const coords = projection([d.LONGITUDE, d.LATITUDE]);
        if (!coords) {
            return false;
        }

        // Cache the projected coordinates
        d.projected = coords;

        // Add a small margin to ensure points are visible
        const margin = 10;
        const [width, height] = [960, 600]; // match SVG dimensions
        if (coords[0] < margin || coords[0] > width - margin || 
            coords[1] < margin || coords[1] > height - margin) {
            return false;
        }
        return true;
    });

    // Create markers with cached projections
    const markers = g.selectAll(".wildfire-marker")
        .data(validData)
        .enter()
        .append("circle")
        .attr("class", "wildfire-marker")
        .attr("cx", d => d.projected[0])
        .attr("cy", d => d.projected[1])
        .attr("r", d => getWildfireRadius(d.fire_size))
        .attr("fill", d => wildfireColorScale(d.fire_size))
        .attr("opacity", 0.5)
        .attr("stroke", "#000")
        .attr("stroke-width", 0.5);
        
    // Add event handlers directly to the markers
    markers.on("mouseover", function(event, d) {
        const selectedMapType = document.querySelector('input[name="map-type"]:checked').id;
        let additionalInfo = '';
        
        // Find weather data for this county
        const countyWeather = wildfireData.find(w => w.fips === event.fips);
        
        if (countyWeather) {
            switch(selectedMapType) {
                case 'temperature-checkbox':
                    if (countyWeather.tmax !== undefined) {
                        additionalInfo = `<br>Temperature: ${formatValue(countyWeather.tmax, 'temperature')}`;
                    }
                    break;
                case 'rain-checkbox':
                    if (countyWeather.prcp !== undefined) {
                        additionalInfo = `<br>Precipitation: ${formatValue(countyWeather.prcp, 'precipitation')}`;
                    }
                    break;
                case 'wind-checkbox':
                    if (countyWeather.wind_speed !== undefined) {
                        additionalInfo = `<br>Wind Speed: ${formatValue(countyWeather.wind_speed, 'wind')}`;
                    }
                    break;
                case 'fuel-checkbox':
                    if (countyWeather.fmc !== undefined) {
                        additionalInfo = `<br>Fuel Moisture: ${formatValue(countyWeather.fmc, 'fuel')}`;
                    }
                    break;
            }
        }

        const tooltipContent = `<strong>Details</strong><br>` +
            `Location: ${fips2County[event.fips]} <br>` +
            `Wildfire Size: ${event.fire_size || 'Unknown'} acres` +
            additionalInfo;
            console.log("fips2County[event.id]", fips2County[event.fips])
            console.log("fips2County[event.id]", event)
        const mouseX = event?.pageX || (d3.event?.pageX) || 0;
        const mouseY = event?.pageY || (d3.event?.pageY) || 0;
        showTooltip(tooltipContent, mouseX, mouseY);
    });
    
    markers.on("mousemove", function(event) {

        const mouseX = event?.pageX || (d3.event?.pageX) || 0;
        const mouseY = event?.pageY || (d3.event?.pageY) || 0;
        
        // Update tooltip position
        const tooltips = document.querySelectorAll(".tooltip-test");
        tooltips.forEach(tooltip => {
            tooltip.style.left = (mouseX + 10) + "px";
            tooltip.style.top = (mouseY - 28) + "px";
        });
    });
    
    markers.on("mouseout", function() {
        hideTooltip();
    });
}

function updateLegend(selectedMapType) {
    // Clear existing legend
    d3.select("#data-legend").html("");
    
    // Show/hide wildfire legend based on checkbox
    document.getElementById('wildfire-legend').style.display = 
        document.getElementById('wildfire-checkbox').checked ? 'block' : 'none';
    
    // Add legend for selected data type
    createDataLegend(selectedMapType);
}

function createDataLegend(selectedMapType) {
    const legend = d3.select("#data-legend");
    legend.html(""); // Clear existing content
    
    if (selectedMapType === 'rain-checkbox') {
        legend.append("p").text("Precipitation legend");
        
        const precipRanges = [
            { range: "0.00 to 0.98 inches", color: "#deebf7" },
            { range: "0.98 to 1.97 inches", color: "#9ecae1" },
            { range: "1.97 to 2.95 inches", color: "#4292c6" },
            { range: ">2.97 inches", color: "#08519c" }
        ];
        
        const items = legend.selectAll(".legend-item")
            .data(precipRanges)
            .enter()
            .append("div")
            .attr("class", "legend-item");
            
        items.append("span")
            .attr("class", "legend-color")
            .style("background-color", d => d.color);
            
        items.append("span")
            .text(d => d.range);
            
    } else if (selectedMapType === 'temperature-checkbox') {
        legend.append("p").text("Temperature legend");
        
        const tempRanges = [
            { range: "32.00 to 47.75 °F", color: "#f2f0f7" },
            { range: "47.75 to 63.50 °F", color: "#cbc9e2" },
            { range: "63.50 to 79.25 °F", color: "#9e9ac8" },
            { range: "79.25 to 95.00 °F", color: "#756bb1" }
        ];
        
        const items = legend.selectAll(".legend-item")
            .data(tempRanges)
            .enter()
            .append("div")
            .attr("class", "legend-item");
            
        items.append("span")
            .attr("class", "legend-color")
            .style("background-color", d => d.color);
            
        items.append("span")
            .text(d => d.range);
    } else {
        // Regular legend for other data types
        const dataTypeLabel = getDataTypeLabel(selectedMapType);
        const scale = selectedMapType === 'wind-checkbox' ? windScale :
                    selectedMapType === 'fuel-checkbox' ? fuelColorScale : null;
        
        if (scale) {
            legend.append("p").text(dataTypeLabel);
            
            const legendData = scale.range().map((color, i) => {
                const d = scale.invertExtent(color);
                return {
                    color: color,
                    value: d[0]
                };
            });

            let measurement = "";

            if (selectedMapType === 'wind-checkbox') {
                measurement = "+ mph";
            } else {
                measurement = "+ tons/acre";
            }
            
            const items = legend.selectAll(".legend-item")
                .data(legendData)
                .enter()
                .append("div")
                .attr("class", "legend-item");
                
            items.append("span")
                .attr("class", "legend-color")
                .style("background-color", d => d.color);
                
            items.append("span")
                .text(d => d.value ? `${d.value.toFixed(1) + measurement}` : "0");
        }
    }
}

// Socket event handlers
socket.on('connect', () => {
    console.log('Socket.IO connected successfully');
});

socket.on('data_broadcast', data => {
    // Validate wildfire data
    wildfireData = (data.wildfire || []).filter(d => {
        if (!d.LATITUDE || !d.LONGITUDE) {
            return false;
        }
        if (d.prcp !== undefined) {
            // Convert prcp to number if it's a string
            if (typeof d.prcp === 'string') {
                d.prcp = parseFloat(d.prcp);
            }
            
        }
        return true;
    });
    // Redraw the map with new data
    redrawMap();
});

socket.on('connect_error', error => {
    console.error('Socket.IO connection error:', error);
});

socket.on('disconnect', reason => {
    console.log('Socket.IO disconnected:', reason);
});

// Update CSS styles
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    #map-container {
        border: 2px solid #000;
        border-radius: 4px;
        padding: 10px;
        background-color: #f8f9fa;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    #wildfire-map {
        width: 100%;
        height: 600px;
        background-color: white;
    }
    
    .county {
        cursor: pointer;
        transition: fill 0.1s;
    }
    .county:hover {
        fill: #666 !important;
    }
    .wildfire-marker {
        cursor: pointer;
        transition: opacity 0.1s;
        will-change: opacity;
    }
    .wildfire-marker:hover {
        opacity: 1 !important;
    }
    .weather-marker {
        cursor: pointer;
        transition: opacity 0.1s;
        will-change: opacity;
    }
    .weather-marker:hover {
        opacity: 1 !important;
    }
`;
document.head.appendChild(styleSheet);
