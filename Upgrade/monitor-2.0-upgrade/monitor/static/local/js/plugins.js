// Avoid `console` errors in browsers that lack a console.
(function() {
  var method;
  var noop = function () {};
  var methods = [
    'assert', 'clear', 'count', 'debug', 'dir', 'dirxml', 'error',
    'exception', 'group', 'groupCollapsed', 'groupEnd', 'info', 'log',
    'markTimeline', 'profile', 'profileEnd', 'table', 'time', 'timeEnd',
    'timeStamp', 'trace', 'warn'
  ];
  var length = methods.length;
  var console = (window.console = window.console || {});

  while (length--) {
    method = methods[length];

    // Only stub undefined methods.
    if (!console[method]) {
        console[method] = noop;
    }
  }
  
}());

// Place any jQuery/helper plugins in here.

jQuery.fn.extend({
  enable: function() {
    return this.each(function() {
      $(this).prop('disabled', false).removeClass('ui-state-disabled');
    });
  },
  disable: function() {
    return this.each(function() {
      $(this).prop('disabled', true).addClass('ui-state-disabled');
    });
  }
});
