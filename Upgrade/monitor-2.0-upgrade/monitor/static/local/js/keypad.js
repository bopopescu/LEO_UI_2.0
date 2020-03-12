(function($) {

    var lastclicktime = new Date().getTime();

    // All of these keypad buttons needs to be the same size. 5 rows and same number of keys/characters per row.
    var keypad_buttons =       [ '1 2 3 4 5 6 7 8 9 0 {bksp}',
                                 'q w e r t y u i o p |',
                                 '{caps} a s d f g h j k l {enter}',
                                 '{shift} z x c v b n m , . {shift}',
                                 '{sym} {clear} {space} {OK} {Cancel}' ];

    var keypad_shift_buttons = [ '! @ # $ % ^ & * ( ) {bksp}',
                                 'Q W E R T Y U I O P \\',
                                 '{caps} A S D F G H J K L {enter}',
                                 '{shift} Z X C V B N M < > {shift}',
                                 '{sym} {clear} {space} {OK} {Cancel}' ];

    var keypad_symbol_buttons = ['1 2 3 4 5 6 7 8 9 0 {bksp}',
                                 '! @ # $ % ^ & * ( ) +',
                                 '{caps} - _ " \' : ; ! [ ] /',
                                 '{shift} ~ ` = \\ , . ? < > {shift}',
                                 '{abc} {clear} {space} {OK} {Cancel}' ];


    function keypad_keypress(target, id, key, keyShift, keySym, options) {
      var clicktime = new Date().getTime();
//      if ((clicktime - lastclicktime) < 200) {
//      lastclicktime = clicktime;
//      return
//    }
      lastclicktime = clicktime;

      // console.log( 'key = ', key )
      if (key == 'undefined')
        return;

      var text = target.val();
      var shift = options.shift;
      var capsLock = options.capsLock;
      var showSymbolsKeys = options.showSymbolsKeys

      var selectionStart = target.get(0).selectionStart;
      var selectionEnd = target.get(0).selectionEnd;
      var key;

      if ( showSymbolsKeys ) key = keySym;
      else key = shift ? keyShift : key;

      switch (key) {
        case '{shift}':
          if (capsLock) capsLock = false;
          shift = !shift;
          break;
        case '{caps}':
          capsLock = !capsLock;
          shift = capsLock;
          break;
        case '{clear}':
          target.val('');
          break;
        case '{bksp}':
          selectionStart = selectionStart <= 0 ? 0 : selectionStart - 1;
          target.val(text.substring(0, selectionStart) + text.substring(selectionEnd));
          break;
        case '{enter}':
          target.val(text.substring(0, selectionStart) + '\n' + text.substring(selectionEnd));
          selectionStart++;
          if (!capsLock)
            shift = false;
          break;
        case '{space}':
          target.val(text.substring(0, selectionStart) + ' ' + text.substring(selectionEnd));
          selectionStart++;
          if (!capsLock)
            shift = false;
          break;
        case '{sym}':
          // Show symbols keyboard
          showSymbolsKeys  = true;
          break;
        case '{abc}':
          // Toggle symbols keyboard
          showSymbolsKeys  = false;
          break;
        case '{blank}':
          // do nothing...
          break;
        default:
          target.val(text.substring(0, selectionStart) + key + text.substring(selectionEnd));
          selectionStart++;
          if (!capsLock)
            shift = false;
          break;
        }

      target.get(0).selectionStart = selectionStart;
      target.get(0).selectionEnd = selectionStart;


      if ( (shift != options.shift) || (showSymbolsKeys != options.showSymbolsKeys) ) {
        for (var idx = 0; idx < keypad_buttons.length; idx++) {
          var rowButtons = keypad_buttons[idx].split(' ');
          var rowShiftButtons = keypad_shift_buttons[idx].split(' ');
          var rowSymbolButtons = keypad_symbol_buttons[idx].split(' ');
          for (var idx2 = 0; idx2 < rowButtons.length; idx2++) {
            if (rowButtons[idx2].indexOf('{') > -1) {
              if ( rowButtons[idx2] == "{sym}" ) {
                var keyid = options.name + '_' + idx.toString() + '_' + idx2.toString();
                if ( showSymbolsKeys == false ) {
                  $('#' + keyid).val("-#$ ");
                  var keyCode = '{sym}';
                }
                else {
                  $('#' + keyid).val("abc");
                  var keyCode = '{abc}';
                }
                $('#' + keyid).prop('key', keyCode );
                $('#' + keyid).prop('keyShift', keyCode );
                $('#' + keyid).prop('keySym', keyCode );
              }
            }
            else {
              var keyid = options.name + '_' + idx.toString() + '_' + idx2.toString();
              if ( showSymbolsKeys == true ) {
                $('#' + keyid).val(rowSymbolButtons[idx2]);
              }
              else {
                $('#' + keyid).val(shift ? rowShiftButtons[idx2] : rowButtons[idx2]);
              }
            }
          }
        }
      }

      // Change key
      if (shift) {
        $('#' + options.name + '_3_0').addClass('ui-state-focus');
        $('#' + options.name + '_3_10').addClass('ui-state-focus');
      } else {
        $('#' + options.name + '_3_0').removeClass('ui-state-focus');
        $('#' + options.name + '_3_10').removeClass('ui-state-focus');
      }

      if (capsLock) {
        $('#' + options.name + '_2_0').addClass('ui-state-focus');
      } else {
        $('#' + options.name + '_2_0').removeClass('ui-state-focus');
      }

      if (showSymbolsKeys) {
        $('#' + options.name + '_4_0').addClass('ui-state-focus');
      } else {
        $('#' + options.name + '_4_0').removeClass('ui-state-focus');
      }

      options.shift = shift;
      options.capsLock = capsLock;
      options.showSymbolsKeys = showSymbolsKeys

    }

    var methods = {
      init : function(settings) {
        var object = $(this);
        settings = $.extend({}, $.fn.keypad.defaults, settings || {})
        settings.name = (Math.random() + 1).toString(36).substring(7);
        object.data('keypad', settings);
        var options = object.data('keypad');

//        console.log( "init: opt Show Sym Keys = ", options.showSymbolsKeys )

        // build up HTML "shell" for keypad.
        object.empty();
        object.addClass('keypad');
        object.append($('<p/>').prop('id', options.name + '_data'));

        // build buttonTable div
        var $buttonTable = $('<div/>');

        // build keys
        for (var idx = 0; idx < keypad_buttons.length; idx++) {
          var rowButtons = keypad_buttons[idx].split(' ');
          var rowShiftButtons = keypad_shift_buttons[idx].split(' ');
          var rowSymbolButtons = keypad_symbol_buttons[idx].split(' ');

          if (idx > 0)
            $buttonTable.append($('<div class="rowspacer"/>'));

          $buttonTable.append($('<span class="endspacer' + idx.toString() + '">&nbsp;</span>'))

          for (var idx2 = 0; idx2 < rowButtons.length; idx2++) {
            var id = options.name + '_' + idx.toString() + '_' + idx2.toString();
            switch (rowButtons[idx2]) {
              case '{OK}':
                $buttonTable.append($('<input type="button"/>').addClass('okCancelWidth').val("OK").button()
                  .click(options, function(e) {
                    if ($.isFunction(e.data.done)) e.data.done(true, $('#' + e.data.name + '_val').val());
                  } ) );
                break;
              case '{Cancel}':
                $buttonTable.append($('<input type="button"/>').addClass('okCancelWidth').val("Cancel").button()
                  .click(options, function(e) {
                    if ($.isFunction(e.data.done)) e.data.done(false, null);
                  } ) );
                break;
              case '{clear}':
                $buttonTable.append($('<button/>').prop('id', id).text('Clear')
                  .button({icons: { primary: 'ui-icon-arrowthickstop-1-w' } } )
                  .click(options, function(e) {
                    keypad_keypress($('#' + options.name + '_val'), id, '{clear}', '{clear}', '{clear}', e.data);
                  } ));
                break;
              case '{bksp}':
                $buttonTable.append($('<button/>').prop('id', id).text('BS')
                  .button({icons: { primary: 'ui-icon-arrowthick-1-w' } } )
                  .click(options, function(e) {
                    keypad_keypress($('#' + options.name + '_val'), id, '{bksp}', '{bksp}', '{bksp}', e.data);
                  } ));
                break;
              case '{shift}':
                $buttonTable.append($('<button/>').prop('id', id).text('Shift')
                  .button({icons: { primary: 'ui-icon-arrowthick-1-n' } } )
                  .click(options, function(e) {
                    keypad_keypress($('#' + options.name + '_val'), id, '{shift}', '{shift}', '{shift}', e.data);
                  } ));
                break;
              case '{enter}':
                $buttonTable.append($('<input type="button"/>').prop('id', id)
                  .prop('key', '{enter}').prop('keyShift', '{enter}').prop('keySym', '{enter}')
                  .val('Enter').button());
                break;
              case '{caps}':
                $buttonTable.append($('<input type="button"/>').prop('id', id)
                  .prop('key', '{caps}').prop('keyShift', '{caps}').prop('keySym', '{caps}')
                  .val('Caps').button());
                break;
              case '{space}':
                $buttonTable.append($('<input type="button"/>').prop('id', id)
                  .prop('key', '{space}').prop('keyShift', '{space}').prop('keySym', '{space}')
                  .addClass('spaceWidth').button());
                break;
              case '{sym}':
                $buttonTable.append($('<input type="button"/>').prop('id', id)
                  .prop('key', '{sym}').prop('keyShift', '{sym}').prop('keySym', '{sym}')
                  .val('-#$ ').button());
                break;
              case '{abc}':
                $buttonTable.append($('<input type="button"/>').prop('id', id)
                  .prop('key', '{abc}').prop('keyShift', '{abc}').prop('keySym', '{abc}')
                  .val('abc').button());
                break;
              case '{blank}':
                $buttonTable.append($('<input type="button"/>').prop('id', id)
                  .prop('key', '{blank}').prop('keyShift', ' ').prop('keySym', ' ')
                  .val('Blank').button());
                break;
              default:
                $buttonTable.append($('<input type="button"/>').prop('id', id)
                  .prop('key', rowButtons[idx2]).prop('keyShift', rowShiftButtons[idx2]).prop('keySym', rowSymbolButtons[idx2] )
                  .addClass('singleWidth').val(rowButtons[idx2]).button());
                break;
            }
          }
        }

        $buttonTable.click(options, function(e) {
          var id = e.target.id;
          // console.log( "click; id->", id )
          if (id.length == 0) return;
          var $key = $('#' + id);
          keypad_keypress($('#' + e.data.name + '_val'), id, $key.prop('key'), $key.prop('keyShift'), $key.prop('keySym'), e.data);
        });

        object.append($('<p/>').append($buttonTable));
        object.hide();

        return object;
      },

      show: function() {
        var object = $(this);
        var options = object.data('keypad');

        if (options.target == null)
          $.error('Target must be specified on keypad');

        var $title = $('<span/>').prop('id', options.name + '_title').addClass('title');
        if (options.title != null) $title.text(options.title);

        var $clone = options.target.clone();
        var cloneid = options.name + '_val';
        $clone.prop('id', cloneid).val(options.target.val());
        $clone.focusout(function() { $('#' + cloneid).focus(); });


        $('#' + options.name + '_data').empty().append($title).append($clone);

        if ($clone.prop('tagName') != 'TEXTAREA')
          $('#' + options.name + '_2_12').hide();
        else
          $('#' + options.name + '_2_12').show();

        object.show();
      },

      hide: function() {
        var object = $(this);
        var options = object.data('keypad');
        object.hide();
      },

      target: function(newTarget) {
        var object = $(this);
        var options = object.data('keypad');
        options.target = $(newTarget);
      },

      title: function(newTitle) {
        var object = $(this);
        var options = object.data('keypad');
        options.title = newTitle;
        $('#' + options.name + '_title').text(options.title);
      },

      unit: function(newUnit) {
        var object = $(this);
        var options = object.data('keypad');
        options.unit = newUnit;
        $('#' + options.name + '_unit').text(options.unit);
      },

      getValue: function() {
        var object = $(this);
        var options = object.data('keypad');
        return $('#' + options.name + '_val').val();
      },

    };


    $.fn.keypad = function(method) {

      if (methods[method]) {
        return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
      } else if (typeof method === 'object' || !method) {
        methods.init.apply(this, arguments);
      } else {
        $.error('Method ' +  method + ' does not exist on keypad');
      }
    };

    $.fn.keypad.defaults = {
      target: null,
      title: null,
      shift: false,
      capsLock: false,
      showSymbolsKeys : false,
      done: null,
    }

})(jQuery);

