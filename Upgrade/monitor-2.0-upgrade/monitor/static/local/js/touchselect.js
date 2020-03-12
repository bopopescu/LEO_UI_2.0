(function($) {

    var methods = {
      init : function(settings) 
      {
        var settings = $.extend({}, $.fn.touchselect.defaults, settings || {});
        return this.each(function () {
          var object = $(this);

          if (!object.data('touchselect')) 
          {
              
            object.data('touchselect', settings);
            var options = object.data('touchselect');
            
            object.wrap('<div class="touchselect"></div>');
            
            var parent = object.parent();        
            parent.prepend('<span>' + object.find('option:selected').text() + '</span><b>&nbsp;</b><i class="icon-chevron-down chevron"></i>');

            // add disable here
            options.disabled = (object.prop('disabled') === true);
            if (options.disabled)
              parent.addClass('disabled');
            else 
              parent.removeClass('disabled');            
            
            if (options.width != null)
            {
              if (options.width == 'select')
                parent.width(object.width());
              else 
                parent.css('width', options.width)
            }
            if (options.height != null)
            {
              if (options.height == 'select')
                parent.height(object.height());
              else 
                parent.css('height', options.height)
            }    
            if (options.minWidth != null)
            {
              if (options.minWidth == 'select')
                parent.css('minWidth', object.css('minWidth'));
              else 
                parent.css('minWidth', options.minWidth);
            }          
            
            parent.click(function () {
              
              var parent = $(this);
              if (parent.hasClass('disabled'))
                return;              
              
              var $screendiv = $('<div class="screendiv"></div>')
              $screendiv.click(function(e) { $(this).remove(); e.stopPropagation(); } );
              
              var $menudiv = $('<div class="menudiv"></div>');
              var $ul = $('<ul></ul>'); 
              
              var numberOfChoices = 0;
              var selectedChoice = 0;
              var object = parent.find('select');
              object.children().each(function(){
                var opttext = $(this).text();
                var optval = $(this).val();
                var $li = $('<li id="' + optval + '">' + opttext + '</li>');
            
                if ($(this).is(':selected'))
                {
                  $li.addClass('selected');
                  selectedChoice = numberOfChoices;
                }
                else 
                {
                  $li.click(function() {
                    var cur = $(this).attr('id');
                    parent.children('span').text($(this).text());
                    object.val(cur);
                    object.trigger('change');
                  });
                }
                $ul.append($li);
                numberOfChoices++;
              });            
              
              
              $menudiv.append($ul);
              $screendiv.append($menudiv);
              parent.append($screendiv);
              
              // goto scroll to here
              var totalHeight = $ul.height();
              var viewHeight = $menudiv.height();
              if (totalHeight > viewHeight)
              {
                var result = Math.round((selectedChoice + 0.5) / numberOfChoices * totalHeight - viewHeight / 2.0);
                if (result < 0) result = 0;
                $menudiv.scrollTop(result);
              }
            });       
    
            object.css('display', 'none');        
          }  
        });
      },
      
      update: function() 
      {
        return this.each(function () {
          var object = $(this);

          if (object.data('touchselect'))
          {      
            var options = object.data('touchselect');
          
            var parent = object.parent();
            var span = parent.children('span');
            span.text(object.find("option:selected").text());
            
            // add disable here
            options.disabled = (object.prop('disabled') === true);
            if (options.disabled)
              parent.addClass('disabled');
            else 
              parent.removeClass('disabled');
          }  
        });
      }

    };


    $.fn.touchselect = function(method) {

      if (methods[method]) {
        return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
      } else if (typeof method === 'object' || !method) {
        methods.init.apply(this, arguments);
      } else {
        $.error('Method ' +  method + ' does not exist on touchselect');
      }       
    }; 
    
    $.fn.touchselect.defaults = {
      width: null,    // null - do nothing, select - set equal to select, else css value
      height: null,
      minWidth: null,
      disabled: false,
    }

})(jQuery); 

