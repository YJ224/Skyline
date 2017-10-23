from webassets import Bundle

from .filters import SimpleClosureJS

BOWER = '../../../ember/bower_components/'

# Font Awesome

fontawesome_css = Bundle(
    BOWER + 'font-awesome/css/font-awesome.css',
    output='css/fontawesome-%(version)s.css')

fontawesome_webfont_eot = Bundle(
    BOWER + 'font-awesome/font/fontawesome-webfont.eot',
    output='font/fontawesome-webfont.eot')

fontawesome_webfont_woff = Bundle(
    BOWER + 'font-awesome/font/fontawesome-webfont.woff',
    output='font/fontawesome-webfont.woff')

fontawesome_webfont_ttf = Bundle(
    BOWER + 'font-awesome/font/fontawesome-webfont.ttf',
    output='font/fontawesome-webfont.ttf')

fontawesome_webfont_svg = Bundle(
    BOWER + 'font-awesome/font/fontawesome-webfont.svg',
    output='font/fontawesome-webfont.svg')


# Twitter Bootstrap

bootstrap_js = Bundle(
    BOWER + 'bootstrap/dist/js/bootstrap.min.js',
    output='js/bootstrap-%(version)s.js')

bootstrap_css = Bundle(
    BOWER + 'bootstrap/dist/css/bootstrap.min.css',
    BOWER + 'bootstrap/dist/css/bootstrap-theme.min.css',
    output='css/bootstrap-%(version)s.js')


# Flot

flot_js = Bundle(
    BOWER + 'Flot/jquery.flot.js',
    BOWER + 'Flot/jquery.flot.time.js',
    BOWER + 'Flot/jquery.flot.crosshair.js',
    BOWER + 'Flot/jquery.flot.resize.js',
    BOWER + 'flot-marks/src/jquery.flot.marks.js',
    filters=SimpleClosureJS(disable_ie_checks=True),
    output='js/flot-%(version)s.js')


# Ember.js

ember_app_js = Bundle(
    'ember/assets/skylines.js',
    output='js/ember-app-%(version)s.js')

ember_vendor_js = Bundle(
    'ember/assets/vendor.js',
    output='js/ember-vendor-%(version)s.js')

ember_app_css = Bundle(
    'ember/assets/skylines.css',
    output='css/ember-app-%(version)s.css')

ember_vendor_css = Bundle(
    'ember/assets/vendor.css',
    output='css/ember-vendor-%(version)s.css')

# SkyLines

main_css = Bundle(
    'vendor/flags/flags.css',
    'vendor/fonts/stylesheet.css',
    filters='cssrewrite',
    output='css/main-%(version)s.css')

all_css = Bundle(
    bootstrap_css,
    main_css,
    fontawesome_css,
    filters='cssmin',
    output='css/skylines-%(version)s.css')

openlayers_css = Bundle(
    'vendor/openlayers/ol.css',
    'css/ol-GraphicLayerSwitcher-v3.css',
    'css/ol-PlayButton.css',
    'css/ol-FullscreenButton.css',
    'css/ol-CesiumSwitcher.css',
    'css/map.css',
    'css/map-infobox.css',
    filters='cssmin, cssrewrite',
    output='css/ol-%(version)s.css')

all_js = Bundle(
    BOWER + 'jquery/jquery.min.js',
    BOWER + 'jQuery-ajaxTransport-XDomainRequest/jquery.xdomainrequest.min.js',
    'vendor/jquery/jquery.timeago.js',
    BOWER + 'sidebar-v2/js/jquery-sidebar.min.js',
    bootstrap_js,
    filters='rjsmin',
    output='js/skylines-%(version)s.js')

upload_js = Bundle(
    BOWER + 'moment/min/moment.min.js',
    BOWER + 'eonasdan-bootstrap-datetimepicker/src/js/bootstrap-datetimepicker.js',
    'js/jquery.flot.flight-upload.js',
    filters=SimpleClosureJS,
    output='js/upload-%(version)s.js')

openlayers_js = Bundle(
    'vendor/openlayers/ol3cesium.js',
    BOWER + 'BigScreen/bigscreen.min.js',
    flot_js,
    upload_js,
    output='js/ol-%(version)s.js')
