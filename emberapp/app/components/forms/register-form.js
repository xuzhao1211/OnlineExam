import Ember from 'ember';
import ValidatedForm from 'misago/components/forms/validated-form';

export default ValidatedForm.extend({
  tagName: 'form',
  classNames: 'form-horizontal',

  zxcvbn: Ember.inject.service('zxcvbn'),

  isLoaded: false,
  loadError: null,
  isBusy: false,

  username: '',
  email: '',
  password: '',

  router: function() {
    return this.container.lookup('router:main');
  }.property(),

  passwordScore: function() {
    return this.get('zxcvbn').scorePassword(this.get('password'), [
      this.get('username'), this.get('email')
    ]);
  }.property('password', 'username', 'email'),

  passwordHelpText: function() {
    if (Ember.$.trim(this.get('password')).length === 0) {
      return null;
    }

    return [
      gettext('Password is very weak.'),
      gettext('Password is weak.'),
      gettext('Password is average.'),
      gettext('Password is strong.'),
      gettext('Password is very strong.')
    ][this.get('passwordScore')];
  }.property('password', 'username', 'email', 'passwordScore'),

  passwordBarWidth: function() {
    this.$('.progress-bar').css('width', ((this.get('passwordScore') + 1) * 20) + '%');
  }.observes('password', 'username', 'email', 'passwordScore'),

  passwordBarClass: function() {
    return 'progress-bar-' + [
      'danger',
      'warning',
      'warning',
      'primary',
      'success'
    ][this.get('passwordScore')];
  }.property('password', 'username', 'email', 'passwordScore'),

  loadServices: function() {
    var self = this;

    var promises = [
      this.get('zxcvbn').load(),
      this.get('captcha').load()
    ];

    Ember.RSVP.allSettled(promises).then(function(array) {
      if (self.isDestroyed) { return; }

      if (array[0].state === 'rejected') {
        self.set('loadError', true);
        console.log('zxcvbn service failed to load.');
      }

      if (array[1].state === 'rejected') {
        self.set('loadError', true);
        console.log('captcha service failed to load.');
      }

      self.set('isLoaded', !self.get('loadError'));
      self.get('captcha').reset();
    });
  }.on('didInsertElement'),

  usernameValidation: function() {
    var state = true;

    var value = Ember.$.trim(this.get('username'));
    var valueLength = value.length;

    var limit = 0;
    var message = null;
    if (valueLength < this.get('settings.username_length_min')) {
      limit = this.get('settings.username_length_min');
      message = ngettext('Username must be at least %(limit)s character long.',
                         'Username must be at least %(limit)s characters long.',
                         limit);
      state = [interpolate(message, {limit: limit}, true)];
    } else if (valueLength > this.get('settings.username_length_max')) {
      limit = this.get('settings.username_length_max');
      message = ngettext('Username cannot be longer than %(limit)s characters.',
                         'Username cannot be longer than %(limit)s characters.',
                         limit);
      state = [interpolate(message, {limit: limit}, true)];
    } else if (!new RegExp('^[0-9a-z]+$', 'i').test(value)) {
      state = [gettext('Username can only contain latin alphabet letters and digits.')];
    }

    if (state === true) {
      this.set('validation.username', 'ok');
    } else {
      this.set('validation.username', state);
    }
  }.observes('username'),

  emailValidation: function() {
    var state = true;

    var value = Ember.$.trim(this.get('email'));
    var valueLength = value.length;

    var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;

    if (valueLength < 4) {
      state = [gettext('Enter valid e-mail address')];
    } else if (!re.test(value)) {
      state = [gettext('Invalid e-mail address.')];
    }

    if (state === true) {
      this.set('validation.email', 'ok');
    } else {
      this.set('validation.email', state);
    }
  }.observes('email'),

  passwordValidation: function() {
    var state = true;

    var valueLength = Ember.$.trim(this.get('password')).length;

    var limit = this.get('settings.password_length_min');
    if (valueLength < limit) {
      var message = ngettext('Valid password must be at least %(limit)s character long.',
                             'Valid password must be at least %(limit)s characters long.',
                             limit);
      state = [interpolate(message, {limit: limit}, true)];
    }

    if (state === true) {
      this.set('validation.password', 'ok');
    } else {
      this.set('validation.password', state);
    }
  }.observes('password'),

  captchaValidation: function() {
    this.set('validation.captcha', undefined);
  }.observes('captcha.value'),

  submit: function() {
    if (this.get('isBusy')) {
      return false;
    }

    var data = {
      username: Ember.$.trim(this.get('username')),
      email: Ember.$.trim(this.get('email')),
      password: Ember.$.trim(this.get('password')),
      captcha: Ember.$.trim(this.get('captcha.value'))
    };

    this.usernameValidation();
    this.emailValidation();
    this.passwordValidation();

    if (this.hasValidationErrors()) {
      this.toast.error(gettext("Form contains errors."));
      return false;
    }

    this.set('isBusy', true);

    var self = this;
    this.ajax.post('users', data
    ).then(function(response) {
      if (self.isDestroyed) { return; }
      self.success(response);
    }, function(jqXHR) {
      if (self.isDestroyed) { return; }
      self.error(jqXHR);
    }).finally(function() {
      if (self.isDestroyed) { return; }
      self.set('isBusy', false);
    });

    return false;
  },

  success: function(responseJSON) {
    this.get('captcha').reset();

    var model = Ember.Object.create(responseJSON);
    model.set('isActive', model.get('activation') === 'active');
    model.set('needsAdminActivation', model.get('activation') === 'activation_by_admin');

    this.modal.show('register-done-modal', model);
  },

  error: function(jqXHR) {
    var rejection = jqXHR.responseJSON;
    if (jqXHR.status === 400) {
      this.toast.error(gettext("Form contains errors."));
      this.get('validation').setProperties(jqXHR.responseJSON);

      if (!this.get('validation.captcha')) {
        this.get('captcha').pass();
      } else {
        this.get('captcha').refresh();
      }
    } else if (jqXHR.status === 403 && typeof rejection.ban !== 'undefined') {
      this.get('router').intermediateTransitionTo('error-banned', rejection.ban);
      this.modal.hide();
    } else {
      this.toast.apiError(jqXHR);
    }
  },

  showTermsFootnote: function() {
    return this.get('settings.terms_of_service') || this.get('settings.terms_of_service_link');
  }.property('settings')
});
