(function($) {

    var renderers = {
      select: function(id, td, row, col, options) {
        var list = options.customOptions[id];
        if (list == null) {
          list = options.columns[col].options;
          if (list == null)
            $.error('jQuery.proptable selects must have options');
        }

        var $sel = $('<select/>').prop('id', id);

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
        var size = 20;
        var columnSize = options.columns[col].size;
        if (columnSize != null)
          size = columnSize;

        var $ret = $('<input/>').prop('id', id).prop('size', size.toString()).val(options.data[row][col])
          .change(function() {
            var c = $('#' + id).val();
            options.data[row][col] = c;
            if ($.isFunction(options.change))
              options.change(row, col, c);
          });

        if ($.isFunction(options.textFocus))
          $ret.click(function() { options.textFocus($ret, row, col); });

        if (options.columns[col].password)
          $ret.prop('type', 'password');
        td.append($ret);

      },

      popup: function(id, td, row, col, options) {
        var clickFunc = options.columns[col].click;
        var val = options.data[row][col];
        td.prop('id', id).css({backgroundColor: val}).html("&#x25E2;")
          .addClass('popup').click(function() { if ($.isFunction(clickFunc)) clickFunc(id, row, col, val); });
      },

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

        td.append($('<input/>').prop('type', 'checkbox').prop('id', id).prop('checked', checked)
          .change(function(e) {
            var c = $('#' + id).is(':checked');
            options.data[row][col] = c;
            if ($.isFunction(options.change))
              options.change(row, col, c);

          })
          .click(function(e) { e.stopPropagation(); } ) );
      },



    }

    var methods = {
      init : function(settings) {
        var object = $(this);
        settings = $.extend({}, $.fn.proptable.defaults, settings || {})
        object.data('pt', settings);

        return object;
      },

      render : function() {

        var object = $(this);
        var options = object.data('pt');

        object.empty();

        if (options !== undefined ) {
          if (options.name === null)
            $.error('jQuery.proptable requires a name to be specified');
          var tableName = options.name;

          var table = $('<table/>').addClass('proptable');

          var numOfColumns = options.columns.length;
          if (options.data.length > 0)
            numOfColumns = Math.min(numOfColumns, options.data[0].length);

          if (options.showHeading) {
            // header
            var elRow = $('<tr/>');

            for (var col = 0; col < numOfColumns; col++) {
              if (options.columns[col].hidden) continue;
              var elCol = $('<th/>').text(options.columns[col].header);
              elRow.append(elCol);
            }
            table.append(elRow);
          }
          table.append(elRow);

          for (var row = 0; row < options.data.length; row++) {
            var elRow = $('<tr/>')
            for (var col = 0; col < numOfColumns; col++) {

              if (options.columns[col].hidden) continue;

              var elCol = $('<td/>');

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
                    $.error('jQuery.proptable columns require a type attribute');
                }

                if (renderers[type])
                  renderers[type].call(this, id, elCol, row, col, options);
                else
                  $.error('jQuery.proptable does not have a type of ' + type);
              }

              elRow.append(elCol);
            }
            table.append(elRow);
          }
          object.append(table);
        }
        else {
          console.log('object is undefined', object );
        }
      },

      update: function(row, col) {
        var object = $(this);
        var options = object.data('pt');

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
        var options = object.data('pt');
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
        var options = object.data('pt');

        if (options.name === null)
          $.error('jQuery.proptable requires a name to be specified');

        var tableName = options.name;
        var id = tableName + "-" + row.toString() + "-" + col.toString();

        options.customOptions[id] = customOptions;
      },

      setCustomType: function(row, col, customType) {
        var object = $(this);
        var options = object.data('pt');

        if (options.name === null)
          $.error('jQuery.proptable requires a name to be specified');

        var tableName = options.name;
        var id = tableName + "-" + row.toString() + "-" + col.toString();
        options.customTypes[id] = customType;
      },

      setRowCustomCss: function(row, newCss) { // This functions sets the CSS for all columns in the row.
        var object = $(this);
        var options = object.data('pt');
        if (options.name === null)
          $.error('jQuery.proptable requires a name to be specified');

        var numOfColumns = options.columns.length;
        var tableName = options.name;

        for (var col = 0; col < numOfColumns; col++) {
          var id = tableName + "-" + row.toString() + "-" + col.toString();
          options.customCss[id] = newCss;
        }
      },

      setCustomCss: function(row, col, newCss) {
        var object = $(this);
        var options = object.data('pt');

        if (options.name === null)
          $.error('jQuery.proptable requires a name to be specified');

        var tableName = options.name;
        var id = tableName + "-" + row.toString() + "-" + col.toString();
        options.customCss[id] = newCss;
      },

      setColumnOptions: function(col, columnOptions) {
        var object = $(this);
        var options = object.data('pt');
        options.columns[col].options = columnOptions;
      },

      addColumnOption: function(col, key, value) {
        var object = $(this);
        var options = object.data('pt');
        options.columns[col][key] = value;
      },

      setColumnClick: function(col, columnFunction) {
        var object = $(this);
        var options = object.data('pt');
        options.columns[col].click = columnFunction;
      },

      loadData: function(newData) {
        var object = $(this);
        var options = object.data('pt');
        options.data = newData;
      },

      getData: function() {
        var object = $(this);
        var options = object.data('pt');
        return options.data;
      },


    };


    $.fn.proptable = function(method) {

      if (methods[method]) {
        return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
      } else if (typeof method === 'object' || !method) {
        methods.init.apply(this, arguments);
      } else {
        $.error('Method ' +  method + ' does not exist on jQuery.proptable');
      }
    };

    $.fn.proptable.defaults = {
      name: null,
      data: [],
      columns: [],
      customOptions: [],
      customTypes: [],
      customCss: [],
      change: null,
      textFocus: null,
      showHeading: true,
    }

})(jQuery);

