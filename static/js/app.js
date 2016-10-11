var map = null;

var campaigns = null;
var journalEntries = null;

var allData = {
    message: "TEST!",
    uploadModalState: false,
    instagramModalState: false,
    modalShow: null,
    showMetaPins: false,
    addingPOI: false,
    financials: {
        "Navigation": [
            ["Garmin Edge 20", "60.00"],
            ["Map of the West Coast", "6.00"],
        ],
        "Camping": [
            ["Buckles", "1.90"],
            ["Etekcity Ultralight Backpacking Stove", "10.99"],
            ["Big Agnes Scout UL2", "149.99"],
            ["REI Kingdom 4 Tent Footprint", "29.83"],
            ["REI Adjustable Tarp Pole", "12.99"],
            ["iPerb Aluminum Tent Stakes (14)", "9.59"],

        ],
        "Bags": [
            ["REI 25 Liter Drybag (w/ $20.00 gift card)", "1.95"],
        ],
        "Bikes": [
            ["Karate Monkey SS Frame (M)", "300.00"],
            ["Karate Monkey Ops (S)", "640.00"],
        ],
        "Sewing Supplies": [
            ["White Chalk", "3.93"],
            ["Small Binder Clips", "3.33"],
            ["Metal Bobbins (15)", "3.99"],
            ["1\" Webbing", "6.88"],
            ["7/8\" Bias Tape", "9.24"],
            ["1\" Plastic Buckles (12)", "4.99"],
            ["Bias Tape Foot for Sewing Machine", "13.99"],
            ["1\" Plastic Triglide Slides (20)", "6.62"],
        ]
    },
    campaigns: null,
    currentCampaign: null,
    journalEntries: null,
}

function _add_gpx(map, url, color, opacity, showMetaPins) {
    var pinsOptions = {
        startIconUrl: '/static/img/pin-icon-start.png',
        endIconUrl: '/static/img/pin-icon-end.png',
        iconUrl: null,
        shadowUrl: null,
        defaultIconURL: '/static/img/marker-icon.png',
        defaultIconShadowURL: '/static/img/marker-icon-shadow.png'
    };

    var noPinsOptions = {
        startIconUrl: null,
        iconUrl: null,
        endIconUrl: null,
        shadowUrl: null,
        defaultIconURL: '/static/img/marker-icon.png',
        defaultIconShadowURL: '/static/img/marker-icon-shadow.png'
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
    for (var ride of rides) {
        var gpx = ride.trackfile;
        _add_gpx(map, gpx, "#FA2A00", 1.0, showMetaPins);
    }

    for (var course of courses) {
        var gpx = course.trackfile;
        _add_gpx(map, gpx, "#000", 0.6, showMetaPins);
    }
}

function create_app() {
    app = new Vue({
        el: "#main_container",
        data: allData,
        methods: {
            changeCampaign: function(idx) {
                app.currentCampaign = app.campaigns[idx];
                erase_map();
                fill_map(app.currentCampaign["ride_set"], app.currentCampaign["course_set"], app.showMetaPins);

            },
            startAddInstagramPOI: function() {
                app.addingPOI = true;
            },
            setCurrentModal: function(name) {
                app.modalShow = name;
            },
            changeUploadModalState: function(state) {
                app.uploadModalState = state;
            },
            changeInstagramModalState: function(state) {
                app.instagramModalState = state;
            },
        },
        computed: {
            financeTotals: function() {
                var total = 0;
                for (var x in this.financials) {
                    for (var y of this.financials[x]) {
                        total += parseFloat(y[1]);
                    }
                }
                return total;
            }
        },
        ready() {
            this.$http.get('/api/blog').then((response) => {
                this.journalEntries = response.data;
                this.currentJournalEntry = null;
                var self = this;

                Vue.nextTick(function() {
                    if (window.location.hash != null) {
                        for (var entry of $(".journalEntry")) {
                            if (window.location.hash == "#" + $(entry).attr("id")) {
                                self.setCurrentModal('journal');
                                Vue.nextTick(function() {
                                    $(entry)[0].scrollIntoView({
                                        behavior: "smooth", // or "auto" or "instant"
                                        block: "start" // or "end"
                                    });
                                });
                            }
                        }
                    }
                });
            }, (response) => {
                // Nope.
            });

            this.$http.get('/api/campaigns').then((response) => {
                this.campaigns = response.data;
                var randomCampaignIDX = Math.floor(Math.random() * this.campaigns.length);
                this.currentCampaign = this.campaigns[randomCampaignIDX];
                this.changeCampaign(randomCampaignIDX);
            }, (response) => {
                // Nope.
            });

            // Add click handler to map
            var self = this;
            onMapClick = function(e) {
                var popup = L.popup();
                if (self.addingPOI) {
                    popup.setLatLng(e.latlng)
                         .setContent("You clicked the map at " + e.latlng.toString())
                         .openOn(map);
                } else {
                    var set = $(".leaflet-popup-close-button");
                    set.each(function(thing) {
                        thing.click();
                    });
                }
            }
            map.on('click', onMapClick);
        }
    });
}

function init() {
    create_map();
    create_app();
}
