import Ember from 'ember';
import PreloadStore from 'misago/services/preload-store';
import Auth from 'misago/services/auth';

export function initialize(container, application) {
  var user = Ember.Object.create(PreloadStore.get('user'));

  // Coerce user ID to string
  if (user.get('id')) {
    user.set('id', user.get('id').toString());
  }

  application.register('misago:user', user, { instantiate: false });
  application.register('misago:isAuthenticated', PreloadStore.get('isAuthenticated'), { instantiate: false });

  application.register('service:auth', Auth, { singleton: true });

  application.inject('service:auth', 'isAuthenticated', 'misago:isAuthenticated');
  application.inject('service:auth', 'user', 'misago:user');
  application.inject('service:auth', 'session', 'store:local');
  application.inject('service:auth', 'store', 'store:main');

  application.inject('route', 'auth', 'service:auth');
  application.inject('controller', 'auth', 'service:auth');
  application.inject('component', 'auth', 'service:auth');
}

export default {
  name: 'auth-service',
  after: 'local-store',
  initialize: initialize
};
