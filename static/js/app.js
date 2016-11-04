// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var map = null;

var campaigns = null;
var journalEntries = null;

var allData = {
    message: "TEST!",
    currentJournalEntry: null,
    uploadModalState: false,
    POIModalState: false,
    modalShow: null,
    showMetaPins: false,
    addingPOI: false,
    poiLatLng: null,
    campaigns: null,
    currentCampaign: null,
    journalEntries: null,
    poiTypes: [
        {value: "instagram", text: "Instagram"},
        {value: "text", text: "Text"},
        {value: "entry", text: "Blog Entry"},
    ],
}

function _add_gpx(map, url, color, opacity, showMetaPins, shouldZoom) {
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
        if (shouldZoom) {
            map.fitBounds(e.target.getBounds());
        }
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

function fill_map(rides, courses, showMetaPins) {
    for (var ride of rides) {
        var gpx = ride.trackfile;
        _add_gpx(map, gpx, "#FA2A00", 1.0, showMetaPins, true);
    }

    for (var course of courses) {
        var gpx = course.trackfile;
        _add_gpx(map, gpx, "#000", 0.6, showMetaPins, false);
    }
}

function close_all_popups() {
    var set = $(".leaflet-popup-close-button");
    set.each(function(thing) {
        thing.click();
    });
}

function delete_all_markers() {
}

function create_app() {
    app = new Vue({
        el: "#main_container",
        data: allData,
        methods: {
            changeCampaign: function(idx) {
                app.currentCampaign = app.campaigns[idx];
                fill_map(app.currentCampaign["ride_set"], app.currentCampaign["course_set"], app.showMetaPins);

            },
            updatePOIs: function() {
                var self = this;
                this.$http.get('/api/instagram_pois').then((response) => {
                    close_all_popups();
                    for (var poi of response.data) {
                        if (poi.cached_response.meta.code == "200") {
                            var imageData = poi.cached_response.data.images;
                            var marker = new L.Marker([poi["poi"]["lat"], poi["poi"]["lng"]], {
                                    icon: L.icon.glyph({
                                        prefix: 'mdi',
                                        glyph: 'panorama'})});
                            map.addLayer(marker);

                            var popup = L.popup()
                                .setContent("<img src=\"" + imageData["thumbnail"]["url"] + "\" />"
                                            + "<p><a href=\"" + poi.cached_response.data.link + "\">Details &raquo;</a></p>"
                                            + "<p>" + poi.cached_response.data.caption.text + "</p>");
                            marker.bindPopup(popup)
                        }
                    };
                }, (response) => {
                    // Nope.
                });

                this.$http.get('/api/entry_pois').then((response) => {
                    close_all_popups();
                    for (var poi of response.data) {
                        var lat = poi["poi"]["lat"];
                        var lng = poi["poi"]["lng"];
                        var marker = new L.Marker([lat, lng], {
                            icon: L.icon.glyph({
                                prefix: 'mdi',
                                glyph: 'book'})});
                        map.addLayer(marker);

                        var self = this;
                        onEntryClick = function(e) {
                            var zoom = 10;
                            map.setView([lat, lng], zoom);

                            self.setCurrentModal('journal');
                            for (var entry of self.journalEntries) {
                                if (poi["entry"]["slug"] == entry.slug) {
                                self.setCurrentJournalEntry(entry);
                                Vue.nextTick(function() {
                                    $(".journalEntryHeaderBlock")[0].scrollIntoView({
                                    behavior: "smooth", // or "auto" or "instant"
                                    block: "start" // or "end"
                                    });
                                });
                                }
                            }
                            if (self.currentJournalEntry == null) {
                                self.setCurrentJournalEntry(self.journalEntries[0]);
                            }
                        }
                        marker.on('click', onEntryClick);
                    };
                }, (response) => {
                    // Nope.
                });

                this.$http.get('/api/text_pois').then((response) => {
                    close_all_popups();
                    for (var poi of response.data) {
                        var lat = poi["poi"]["lat"];
                        var lng = poi["poi"]["lng"];
                        var marker = new L.Marker([lat, lng], {
                            icon: L.icon.glyph({
                                prefix: 'mdi',
                                glyph: 'eye'})});
                        map.addLayer(marker);

                        var popup = L.popup() .setContent(poi.text);
                        marker.bindPopup(popup)
                    };
                }, (response) => {
                    // Nope.
                });
            },
            setCurrentJournalEntry: function(journalEntry) {
                this.currentJournalEntry = journalEntry;
            },
            submitPOI: function(e) {
                var latLng = app.poiLatLng;
                var shortcode = app.poiShortcode;
                var type = app.poiType;
                var text = app.poiText;
                var csrftoken = getCookie('csrftoken');
                var data = {
                    latlng: latLng,
                    shortcode: shortcode,
                    type: type,
                    text: text
                };
                var self = this;

                this.$http.post('/add_poi/', data, {headers: {"X-CSRFToken": csrftoken}}).then((response) => {
                    self.updatePOIs();
                }, (response) => {
                    // Nope.
                });
            },
            setCurrentModal: function(name) {
                app.modalShow = name;
            },
            changeUploadModalState: function(state) {
                app.uploadModalState = state;
            },
            changePOIModalState: function(state) {
                app.addingPOI = true;
                app.poiLatLng = "Select point of interest...";
                app.POIModalState = state;
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
                        for (var entry of self.journalEntries) {
                            if (window.location.hash == "#" + entry.slug) {
                                self.setCurrentJournalEntry(entry);
                                self.setCurrentModal('journal');
                                Vue.nextTick(function() {
                                    $(".journalEntryHeaderBlock")[0].scrollIntoView({
                                        behavior: "smooth", // or "auto" or "instant"
                                        block: "start" // or "end"
                                    });
                                });
                            }
                        }
                        if (self.currentJournalEntry == null) {
                            self.setCurrentJournalEntry(self.journalEntries[0]);
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

            this.updatePOIs();

            // Add click handler to map
            var self = this;
            onMapClick = function(e) {
                if (self.addingPOI) {
                    self.poiLatLng = e.latlng;
                    self.addingPOI = false;
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


