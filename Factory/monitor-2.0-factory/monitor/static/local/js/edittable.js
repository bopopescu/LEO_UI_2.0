(function($) {

    var renderers = {
      checkbox: function(id, td, row, col, options) {
        td.addClass('checkbox').click(function() {
          var $e = $('#' + id);
          var c = ! $e.is(':checked');
          $e.prop('checked', c);
          options.data[row][col] = c;
          if ($.isFunction(options.change))
            options.change(row, col, c);
        });

        var checked = options.data[row][col];
        if (typeof checked != 'boolean')
          checked = (checked == 'true' ? true : false);

        td.append($('<input/>').prop('type', 'checkbox').prop('id', id)
          .prop('checked', checked).prop('disabled', options.disabled)
          .change(function(e) {
            var c = $('#' + id).is(':checked');
            options.data[row][col] = c;
            if ($.isFunction(options.change))
              options.change(row, col, c);

          })
          .click(function(e) { e.stopPropagation(); } ) );
      },

      select: function(id, td, row, col, options) {
        var list = options.customOptions[id];
        if (list == null) {
          list = options.columns[col].options;
          if (list == null)
            $.error('jQuery.edittable selects must have options');
        }

        var $sel = $('<select/>').prop('id', id).prop('disabled', options.disabled);

        try {
          for (var idx = 0; idx < list.length; idx++) {
            if (typeof list[idx] === 'string') {
                $sel.append($('<option/>').val(list[idx]).text(list[idx]));
            } else {
              for (var key in list[idx])
                $sel.append($('<option/>').val(key).text(list[idx][key]));
            }
          }
        }
        catch(err) {
          $.error('jQuery.edittable options must be either strings or objects with a { val: text } format');
        }

        $sel.val(options.data[row][col]);
        if ($sel.val() == null)
          options.data[row][col] = $sel.children(":first").val();

        $sel.change(function() {
          var c = $('#' + id).val();
          options.data[row][col] = c;
          if ($.isFunction(options.change))
            options.change(row, col, c);
        });
        td.append($sel);
      },

      text: function(id, td, row, col, options) {
        var size = 20; // default size
        var placeholder = options.columns[col].placeholder;
        var columnSize = options.columns[col].size;
        var header = options.columns[col].header
        if (columnSize != null)
          size = columnSize;


        if ( options.customCss[id] != null ) {
          customProp = options.customCss[id]
          var $ret = $('<input/>').prop('id', id).prop('size', size.toString()).prop(customProp).val(options.data[row][col])
            .change(function() {
              var c = $('#' + id).val();
              options.data[row][col] = c;
              if ($.isFunction(options.change))
                options.change(row, col, c);
            });
        }
        else
        {
          var $ret = $('<input/>').prop('id', id).prop('size', size.toString()).val(options.data[row][col])
            .change(function() {
              var c = $('#' + id).val();
              options.data[row][col] = c;
              if ($.isFunction(options.change))
                options.change(row, col, c);
            });
        }

        if ( options.placeholder[id] != null ) {
          customProp = options.placeholder[id];
          var $ret = $('<input/>').prop('id', id).prop('placeholder', placeholder.toString()).prop(customProp).val(options.data[row][col])
            .change(function() {
              var c = $('#' + id).val();
              options.data[row][col] = c;
              if ($.isFunction(options.change))
                options.change(row, col, c);
            });
        }

        else
        {
          if (header == "Address")
		  {
		  var placeholder = "Enter Device Address";
		  }
          else{
		  var placeholder = "Less than 20 Characters"; 
		  }
          var $ret = $('<input/>').prop('id', id).prop('placeholder', placeholder.toString()).val(options.data[row][col])
            .change(function() {
              var c = $('#' + id).val();
              options.data[row][col] = c;
              if ($.isFunction(options.change))
                options.change(row, col, c);
            });
        }


        if ($.isFunction(options.textFocus))
          $ret.click(function() { options.textFocus($ret, row, col); });

        if (options.customOptions[id] != null )
          $ret.prop( options.customOptions[id] );

          if (options.columns[col].password)
          $ret.prop('type', 'password');
        td.append($ret);
      },

      color: function(id, td, row, col, options) {
        var clickFunc = options.columns[col].click;
        var val = options.data[row][col];
        td.prop('id', id).css({backgroundColor: val}).html("&#x25E2;")
          .addClass('color').click(function() { if ($.isFunction(clickFunc)) clickFunc(id, row, col, val); });
      },

      file: function(id, td, row, col, options) {
        var clickFunc = options.columns[col].click;
        var val = options.data[row][col];
        td.prop('id', id).html("&#x25E2;&nbsp;" + options.data[row][col].toString())
          .addClass('file').click(function() { if ($.isFunction(clickFunc)) clickFunc(id, row, col, val); });
      },

    }

    var methods = {
      init : function(settings) {
        var object = $(this);
        settings = $.extend({}, $.fn.edittable.defaults, settings || {})
        object.data('et', settings);

        return object;
      },


      render : function() {

        var object = $(this);
        var options = object.data('et');

        object.empty();

        if (options.name === null)
          $.error('jQuery.edittable requires a name to be specified');
        var tableName = options.name;

        var table = $('<table/>').addClass('edittable');
        if ( options.tableCss != null )
          table.css( options.tableCss )

        // header
        var numOfColumns = options.columns.length;
        if (options.data.length > 0)
          numOfColumns = Math.min(numOfColumns, options.data[0].length);

        if (options.showHeading) {
          var elRow = $('<tr/>');
          for (var col = 0; col < numOfColumns; col++) {
            var elCol = $('<th/>').text(options.columns[col].header);
            elRow.append(elCol);
          }
          table.append(elRow);
        }

        for (var row = 0; row < options.data.length; row++) {
          var elRow = $('<tr/>')
          for (var col = 0; col < numOfColumns; col++) {

            var elCol = $('<td/>');

            var type = options.columns[col].type;
            if (type == null)
              $.error('jQuery.edittable columns require a type attribute');

            var id = tableName + "-" + row.toString() + "-" + col.toString();

            if (options.columns[col].readonly) {
              var elDiv = $('<div class="readonly"/>').prop('id', id).html(options.data[row][col])

              var css = options.customCss[id];
              if (css != null) elDiv.css( css );
              elCol.append(elDiv);
            } else {

              var type = options.customTypes[id];
              if (type == null) {
                type = options.columns[col].type;
                if (type == null)
                  $.error('jQuery.edittable columns require a type attribute');
              }
            }

            if (renderers[type])
              renderers[type].call(this, id, elCol, row, col, options);
            else
              $.error('jQuery.edittable does not have a type of ' + type);

            elRow.append(elCol);
          }
          table.append(elRow);
        }

        object.append(table);

      },

      update: function(row, col) {
        var object = $(this);
        var options = object.data('et');

        var id = options.name + "-" + row.toString() + "-" + col.toString();

        if (options.columns[col].readonly) {
          $('#' + id).html(options.data[row][col])

          var css = options.customCss[id];
          if (css != null) $('#' + id).css( css );
        } else {
          $('#' + id).val(options.data[row][col]);
        }
      },

      updateAll: function(row, col) {
        var object = $(this);
        var options = object.data('et');
        var name = options.name;

        var numOfColumns = options.columns.length;
        if (options.data.length > 0)
          numOfColumns = Math.min(numOfColumns, options.data[0].length);

        for (var row = 0; row < options.data.length; row++) {
          for (var col = 0; col < numOfColumns; col++) {
            var id = options.name + "-" + row.toString() + "-" + col.toString();
            if (options.columns[col].readonly) {
              $('#' + id).html(options.data[row][col])

              var css = options.customCss[id];
              if (css != null) $('#' + id).css( css );
            } else {
              $('#' + id).val(options.data[row][col]);
            }
          }
        }
      },

      setCustomOptions: function(row, col, customOptions) {
        var object = $(this);
        var options = object.data('et');

        if (options.name === null)
          $.error('jQuery.edittable requires a name to be specified');

        var tableName = options.name;
        var id = tableName + "-" + row.toString() + "-" + col.toString();

        options.customOptions[id] = customOptions;
      },

      setCustomType: function(row, col, customType) {
        var object = $(this);
        var options = object.data('et');

        if (options.name === null)
          $.error('jQuery.proptable requires a name to be specified');

        var tableName = options.name;
        var id = tableName + "-" + row.toString() + "-" + col.toString();
        options.customTypes[id] = customType;
      },


      setCustomCss: function(row, col, newCss) {
        var object = $(this);
        var options = object.data('et');

        if (options.name === null)
          $.error('jQuery.edittable requires a name to be specified');

        var tableName = options.name;
        var id = tableName + "-" + row.toString() + "-" + col.toString();
        options.customCss[id] = newCss;
      },

      setPlaceHolder: function(row, col, placeholder) {
        var object = $(this);
        var placeholder = "Less Than 20 Characters";
        var options = object.data('et');

        if (options.name === null)
          $.error('jQuery.edittable requires a name to be specified');

        var tableName = options.name;
        var id = tableName + "-" + row.toString() + "-" + col.toString();
        options.placeholder[id] = placeholder;
      },

      setColumnOptions: function(col, columnOptions) {
        var object = $(this);
        var options = object.data('et');
        options.columns[col].options = columnOptions;
      },

      addColumnOption: function(col, key, value) {
        var object = $(this);
        var options = object.data('et');
        options.columns[col][key] = value;
      },

      setColumnClick: function(col, columnFunction) {
        var object = $(this);
        var options = object.data('et');
        options.columns[col].click = columnFunction;
      },


      getColumnHeader: function(col) {
        var object = $(this);
        var options = object.data('et');
        return options.columns[col].header;
      },

      loadData: function(newData) {
        var object = $(this);
        var options = object.data('et');
        options.data = newData;
      },

      getData: function() {
        var object = $(this);
        var options = object.data('et');
        return options.data;
      },

      disabled: function(state) {
        var object = $(this);
        var options = object.data('et');
        var newState = (state === true)
        if (options.disabled !== newState) {
          options.disabled = newState;
          object.edittable('render');
        }
      }

    };


    $.fn.edittable = function(method) {

      if (methods[method]) {
        return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
      } else if (typeof method === 'object' || !method) {
        methods.init.apply(this, arguments);
      } else {
        $.error('Method ' +  method + ' does not exist on jQuery.edittable');
      }
    };

    $.fn.edittable.defaults = {
      name: null,
      data: [],
      columns: [],
      customOptions: [],
      customTypes: [],
      customCss: [],
      placeholder:[],
      change: null,
      textFocus: null,
      disabled: false,
      showHeading: true,
      tableCss: null
    }

})(jQuery);

