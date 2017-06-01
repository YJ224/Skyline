import Ember from 'ember';

export default Ember.Object.extend(Ember.Evented, {
  map: null,
  flights: null,
  hover_enabled: true,

  init() {
    this._super(...arguments);

    let map = this.get('map');

    map.on('pointermove', e => {
      if (!this.get('hover_enabled') || e.dragging)
        return;

      var coordinate = map.getEventCoordinate(e.originalEvent);
      this.displaySnap(coordinate);
    });
  },

  setMode(mode) {
    this.set('hover_enabled', mode);
  },

  displaySnap(coordinate) {
    let flights = this.get('flights');
    let map = this.get('map');

    var flight_path_source = flights.getSource();

    var closest_feature = flight_path_source
        .getClosestFeatureToCoordinate(coordinate);

    if (closest_feature !== null) {
      var geometry = closest_feature.getGeometry();
      var closest_point = geometry.getClosestPoint(coordinate);

      var feature_pixel = map.getPixelFromCoordinate(closest_point);
      var mouse_pixel = map.getPixelFromCoordinate(coordinate);

      var squared_distance = Math.pow(mouse_pixel[0] - feature_pixel[0], 2) +
                             Math.pow(mouse_pixel[1] - feature_pixel[1], 2);

      if (squared_distance > 100) {
        this.trigger('set_time', null);
      } else {
        var time = closest_point[3];
        this.trigger('set_time', time);
      }
    }

    map.render();
  },
});
