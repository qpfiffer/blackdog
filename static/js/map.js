var layer = L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {});

var map = L.map('map', {
    scrollWheelZoom: true,
    center: [45.5231, -122.6765],
    zoomControl: false,
    zoom: 9,
});

map.addLayer(layer);

var rides = ['671E4342', '671C3011'];
for (var idx in rides) {
    var ride = rides[idx];
    var gpx = '/data/rides/' + ride + '.gpx';
    var thing = new L.GPX(gpx, { async: true,
        polyline_options: {
            color: '#FA2A00',
        opacity: 1.0,
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
