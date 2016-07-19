var map = null;
function _add_gpx(map, url, color, opacity, showMetaPins) {
    var pinsOptions = {
        startIconUrl: '/static/img/pin-icon-start.png',
        endIconUrl: '/static/img/pin-icon-end.png',
        iconUrl: null,
        shadowUrl: null
    };

    var noPinsOptions = {
        startIconUrl: null,
        iconUrl: null,
        endIconUrl: null,
        shadowUrl: null
    };

    var thing = new L.GPX(url, { async: true,
        polyline_options: {
            color: color,
        opacity: opacity,
        },
        marker_options: !!showMetaPins ? pinsOptions : noPinsOptions,
    }).on('loaded', function(e) {
        map.fitBounds(e.target.getBounds());
    }).addTo(map);
}

function create_map() {
    map = L.map('map', {
        scrollWheelZoom: true,
        center: [45.5231, -122.6765],
        zoomControl: false,
        zoom: 9,
    });

    var layer = L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {});
    map.addLayer(layer);
}

function erase_map() {
}

function fill_map(rides, courses, showMetaPins) {
    for (var idx in rides) {
        var ride = rides[idx];
        var gpx = '/data/rides/' + ride + '.gpx';
        _add_gpx(map, gpx, "#FA2A00", 1.0, showMetaPins);
    }

    for (var idx in courses) {
        var course = courses[idx];
        var gpx = '/data/courses/' + course + '.gpx';
        _add_gpx(map, gpx, "#000", 0.6, showMetaPins);
    }
}

function create_app() {
    var campaigns = [
        {
            name: "Home to Milo 7/9/16",
            rides: ['679G1357', '67A82825', '67AA3532'],
            courses: ['Home_to_Milo'],
        },
    ];

    app = new Vue({
        el: "#main_container",
        data: {
            message: "TEST!",
            modalShow: null,
            showMetaPins: false,
            financials: [
                ["Buckles", "1.90"],
                ["Garmin Edge 20", "60.00"],
                ["Map of the West Coast", "6.00"]
            ],
            campaigns: campaigns,
            currentCampaign: campaigns[0]
        },
        methods: {
            changeCampaign: function(idx) {
                app.currentCampaign = app.campaigns[idx];
                erase_map();
                fill_map(app.currentCampaign["rides"], app.currentCampaign["courses"], app.showMetaPins);

            },
            setCurrentModal: function(name) {
                app.modalShow = name;
            },
        },
        computed: {
            financeTotals: function() {
                var total = 0;
                for (var x of this.financials) {
                    total += parseFloat(x[1]);
                }
                return total;
            }
        }
    });
}

function init() {
    create_map();
    create_app();
    app.changeCampaign(0);
}
