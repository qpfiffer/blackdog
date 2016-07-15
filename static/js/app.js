function _add_gpx(map, url, color, opacity) {
    var thing = new L.GPX(url, { async: true,
        polyline_options: {
            color: color,
        opacity: opacity,
        },
        marker_options: {
            //startIconUrl: '/static/img/pin-icon-start.png',
            //endIconUrl: '/static/img/pin-icon-end.png',
            //shadowUrl: '/static/img/pin-shadow.png'
            startIconUrl: null,
        endIconUrl: null,
        shadowUrl: null
        }
    }).on('loaded', function(e) {
        map.fitBounds(e.target.getBounds());
    }).addTo(map);
}

function create_map() {
    var layer = L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {});

    var map = L.map('map', {
        scrollWheelZoom: true,
        center: [45.5231, -122.6765],
        zoomControl: false,
        zoom: 9,
    });

    map.addLayer(layer);

    var rides = ['67A82825', '67AA3532'];
    for (var idx in rides) {
        var ride = rides[idx];
        var gpx = '/data/rides/' + ride + '.gpx';
        _add_gpx(map, gpx, "#FA2A00", 1.0);
    }

    var courses = ['Home_to_Milo'];
    for (var idx in courses) {
        var course = courses[idx];
        var gpx = '/data/courses/' + course + '.gpx';
        _add_gpx(map, gpx, "#002A00", 0.6);
    }
}

function create_app() {
    app = new Vue({
        el: "#main_container",
        data: {
            message: "TEST!",
            modalShow: null,
            financials: [
                ["Buckles", "1.90"],
                ["Garmin Edge 20", "60.00"],
                ["Map of the West Coast", "6.00"]
            ],
        },
        methods: {
            setCurrentModal: function(name) {
                app.modalShow = name;
            }
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
}
