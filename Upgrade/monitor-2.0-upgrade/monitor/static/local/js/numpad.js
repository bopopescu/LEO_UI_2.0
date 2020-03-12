(function($) {

    var lastclicktime = new Date().getTime();
    
    function numpad_keypress(target, key) {
      var clicktime = new Date().getTime();
      if ((clicktime - lastclicktime) < 200) {
        lastclicktime = clicktime;
        return
      }      
      lastclicktime = clicktime;
            
      if (key == 'undefined')
        return;
      
      var text = target.val().trim();

      switch (key) {
        case '{clear}':
          target.val('');
          break;
        case '{bksp}':
          var len = text.length - 1;
          target.val(text.substring(0, len));
          break;
        case '{plusminus}':
          if (text.substring(0,1) == '-') text = text.substring(1);
          else text = '-' + text;
          target.val(text);
          break;
        default:
          target.val(text + key)
          break;
        }
    }

    var methods = {
      init : function(settings) {
        var object = $(this);
        settings = $.extend({}, $.fn.numpad.defaults, settings || {})
        settings.name = (Math.random() + 1).toString(36).substring(7);
        object.data('numpad', settings);
        var options = object.data('numpad');
        
        object.empty();  
        object.addClass('numpad');
        var $dataSection = $('<p/>');

        var $title = $dataSection.append($('<span/>').prop('id', options.name + '_title').addClass('title'));
        if (options.title != null) $title.text(options.title);
        
        $dataSection.append($('<input type="text"/>').prop('id', options.name + '_val'));

        var $unit = $dataSection.append($('<span/>').prop('id', options.name + '_unit').addClass('unit'));
        if (options.unit != null) $unit.text(' ' + options.unit);        
        
        object.append($dataSection);
        
        var buttons = ['7 8 9 {bksp}',
                       '4 5 6 {clear}',
                       '1 2 3',
                       '0 . {plusminus}' ];

        var $buttonTable = $('<table/>');
        
        for (var idx = 0; idx < buttons.length; idx++) {
          var row = buttons[idx];
          var rowButtons = row.split(' ');          
          var $tr = $('<tr/>');
          for (var idx2 = 0; idx2 < rowButtons.length; idx2++) {
            var $td = $('<td/>');
            var id = options.name + '_' + rowButtons[idx2];
            switch (rowButtons[idx2]) {
              case '{clear}':
                $td.append($('<button/>').prop('id', id).addClass('specialWidth').text('Clear')
                  .button({icons: { primary: 'ui-icon-arrowthickstop-1-w' } } )
                  .click(function() { numpad_keypress($('#' + options.name + '_val'), '{clear}' )} ));
                break;
              case '{bksp}':
                $td.append($('<button/>').prop('id', id).addClass('specialWidth').text('BS')
                  .button({icons: { primary: 'ui-icon-arrowthick-1-w' } } )
                  .click(function() { numpad_keypress($('#' + options.name + '_val'), '{bksp}' )} ));
                break;
              case '{plusminus}':
                $td.append($('<input type="button"/>').prop('id', id).addClass('singleWidth')
                  .val($('<div/>').html('&plusmn;').text()).button());
                break;
              default:
                $td.append($('<input type="button"/>').prop('id', id).addClass('singleWidth')
                  .val(rowButtons[idx2]).button());
                break;
            }
            $tr.append($td);
          }
          $buttonTable.append($tr);
        }

        $buttonTable.click(function(e) {
          var id = e.target.id;
          if (id.length == 0) return;
          
          var key = id.split('_');
          if (key.length != 2) return;
          var key = key[1];
          
          numpad_keypress($('#' + options.name + '_val'), key);
        });        
        
        object.append($('<p/>').append($buttonTable));
        object.hide();
        
        return object;
      }, 

      show: function() {
        var object = $(this);
        var options = object.data('numpad');
        
        val = '0';
        if (options.target != null) 
          val = options.target.val();

        $('#' + options.name + '_val').val(val).focusout(function() { $('#' + options.name + '_val').focus(); });

        object.show();
      },

      hide: function() {
        var object = $(this);
        var options = object.data('numpad');
        object.hide();
      },      

      target: function(newTarget) {
        var object = $(this);
        var options = object.data('numpad');
        options.target = $(newTarget);
      },
      
      title: function(newTitle) {
        var object = $(this);
        var options = object.data('numpad');
        options.title = newTitle;
        $('#' + options.name + '_title').text(options.title);
      },
      
      unit: function(newUnit) {
        var object = $(this);
        var options = object.data('numpad');
        options.unit = newUnit;
        $('#' + options.name + '_unit').text(options.unit);
      },      

      getValue: function() {
        var object = $(this);
        var options = object.data('numpad');
        return $('#' + options.name + '_val').val();
      },
      
    };


    $.fn.numpad = function(method) {

      if (methods[method]) {
        return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
      } else if (typeof method === 'object' || !method) {
        methods.init.apply(this, arguments);
      } else {
        $.error('Method ' +  method + ' does not exist on numpad');
      }       
    }; 
    
    $.fn.numpad.defaults = {
      target: null,
      title: null,
      unit: null,
    }

})(jQuery); 

