//http://stefangabos.ro/jquery/jquery-plugin-boilerplate-revisited/
(function($) {

  $.selection = function(element, options) {

    var defaults = {
      touchEnabled: false,
      onSelect: function(x1, y1, x2, y2) { alert(x1 + ',' + y1 + ',' + x2 + ',' + y2) },
      css: {border: '1px solid rgba(232, 207, 172, .8)', backgroundColor: 'rgba(232, 207, 172, .4)', zIndex: 100	},
      transformPoints: true,
      selectionThreshold: 3,
    }
    
    var plugin = this;
    plugin.settings = {}
    var $element = $(element), element = element;

    var selection = {
      first: { x: -1, y: -1}, 
      second: { x: -1, y: -1},
      active: false,
      touch: false,
      $div: null,
    };
    var savedhandlers = {};            
    var mouseUpHandler = null;  
        
    plugin.init = function() {
      plugin.settings = $.extend({}, defaults, options);

      selection.$div = $('<div style="position: absolute" >').hide().mousemove(function(e) { onMouseMove(e); });      
      if (plugin.settings.css != null) 
        selection.$div.css(plugin.settings.css);
      $element.after(selection.$div);
      
      $element.mousemove(onMouseMove);
      $element.mousedown(onMouseDown);
      $element.bind('touchstart', function(e) {
          // Using a touch device, disable mouse events to prevent 
          // event handlers being called twice
          $element.unbind('mousedown', onMouseDown);
          onMouseDown(e);
          });
      $element.bind('touchmove', onMouseMove);  
    }

    
    function setPosition(t, e) {
      var coordHolder = selection.touch ? e.originalEvent.changedTouches[0] : e;          
      t.x = coordHolder.pageX;
      t.y = coordHolder.pageY;
    }
        
    function updateSelection(e) {
      if ((selection.touch ? e.originalEvent.changedTouches[0] : e).pageX == null)
        return;  
      setPosition(selection.second, e);

      var $div = selection.$div;
      
      var x1 = selection.first.x;
      var y1 = selection.first.y;
      var x2 = selection.second.x;
      var y2 = selection.second.y;

      if (x1 > x2) { var tmp=x1; x1=x2; x2=tmp; }
      if (y1 > y2) { var tmp=y1; y1=y2; y2=tmp; }
      
      if (!$div.is(':visible'))
        $div.show();
      
      $div.offset({left: x1, top: y1});
      $div.width(x2-x1);
      $div.height(y2-y1);
      
    }            
  
    function onMouseMove(e) {
      if (selection.active) {
        updateSelection(e);
        if (selection.touch == true) { e.preventDefault(); }                
      }
    }
  
    function onMouseDown(e) {
      if (e.type == 'touchstart' && e.originalEvent.touches.length == 1) { // only accept single touch
        if (plugin.settings.touchEnabled) selection.touch = true;
      } else if (e.which != 1 || e.originalEvent.touches && e.originalEvent.touches.length > 1) { // only accept left-click
        return;
      }
      
      // cancel out any text selections
      document.body.focus();
  
      // prevent text selection and drag in old-school browsers
      if (document.onselectstart !== undefined && savedhandlers.onselectstart == null) {
        savedhandlers.onselectstart = document.onselectstart;
        document.onselectstart = function () { return false; };
      }
      if (document.ondrag !== undefined && savedhandlers.ondrag == null) {
        savedhandlers.ondrag = document.ondrag;
        document.ondrag = function () { return false; };
      }
  
      setPosition(selection.first, e);
      selection.active = true;
  
      // this is a bit silly, but we have to use a closure to be
      // able to whack the same handler again
      mouseUpHandler = function (e) { onMouseUp(e); };
      
      $(document).one(selection.touch ? "touchend" : "mouseup", mouseUpHandler);
    }
  
    function onMouseUp(e) {
      if (selection.active) {
        mouseUpHandler = null;
        updateSelection(e);
  
        selection.$div.hide();
        selection.active = false;
        selection.touch = false;

        var x1 = selection.first.x;
        var y1 = selection.first.y;
        var x2 = selection.second.x;
        var y2 = selection.second.y;  
        
        if (plugin.settings.transformPoints) {
          if (x1 > x2) { var tmp=x1; x1=x2; x2=tmp; }
          if (y1 > y2) { var tmp=y1; y1=y2; y2=tmp; }
        }      
        
        if ((Math.abs(x1-x2) > plugin.settings.selectionThreshold) && (Math.abs(y1-y2) > plugin.settings.selectionThreshold)) {
          var offsetLeft = $element.offset().left;
          var offsetTop = $element.offset().top;
    
          if ($.isFunction(plugin.settings.onSelect))
            plugin.settings.onSelect(x1 - offsetLeft, y1 - offsetTop, x2 - offsetLeft, y2 - offsetTop);
        }
        
      }      
      //return false;
    }
    
    plugin.cancel = function() {
      mouseUpHandler = null;
      selection.$div.hide();
      selection.active = false;
      selection.touch = false;      
    }    
    
    plugin.init();

  }

  $.fn.selection = function(options) {

    return this.each(function() {
        if (undefined == $(this).data('selection')) {
            var plugin = new $.selection(this, options);
            $(this).data('selection', plugin);
        }
    });

}

})(jQuery);
