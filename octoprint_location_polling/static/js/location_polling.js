$(function() {
    function LPViewModel(parameters) {
        var self = this;

        self.pos_html = ko.observable("unknown position");

        self.onEventPositionUpdate = function(payload) {
          s2 = "X: <b>" + payload.x + "</b>&nbsp;&nbsp;&nbsp;Y: <b>" + payload.y + "</b>&nbsp;&nbsp;&nbsp;Z: <b>" + payload.z + "</b>";
          self.pos_html(s2);
        }
        
        self.refresh = function() {
          // when clicked, we'll hit this API to manually perform M114 which should update us through onEventPositionUpdate
          $.get('/api/plugin/location_polling');
        }
    }

    OCTOPRINT_VIEWMODELS.push([
        LPViewModel,  // constructor
        [],  // dependencies (none)
        ["#navbar_plugin_location_polling"]  // elements to bind to
    ]);
});