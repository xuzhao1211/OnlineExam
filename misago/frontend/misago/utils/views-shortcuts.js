(function (Misago) {
  'use strict';

  Misago.loadingPage = function(_) {
    return m('.page.page-loading', _.component(Misago.Loader));
  };
} (Misago.prototype));
