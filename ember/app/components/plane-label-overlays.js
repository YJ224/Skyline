import Ember from 'ember';

export default Ember.Component.extend({
  fixCalc: Ember.inject.service(),

  tagName: '',

  map: null,

  fixes: Ember.computed.readOnly('fixCalc.fixes'),
});
