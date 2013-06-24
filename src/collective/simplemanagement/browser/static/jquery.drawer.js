(function($) {
    var Drawer = function(element, options) {
        this.options = {
            action: "click",
            group: null,
            content: null,
            structure: "<div />",
            css_class: "drawer",
            open: false,
            position: "bottom",
            offset: [0, 0],
            remove: true
        };
        this.trigger = $(element);
        for(var option in this.options) {
            var value = this.trigger.attr('data-'+option);
            if(value) this.options[option] = value;
        }
        $.extend(this.options, options);
        if((typeof this.options.offset) === "string")
            this.options.offset = this.options.offset.split(",");
        this.drawer = null;
        var self = this;
        this.trigger.bind(this.options.action, function(e) {
            e.preventDefault();
            if(self.isShown(true))
                self.hide();
            else {
                if(self.options.group)
                    $(self.options.group).drawer('hide');
                self.show();
            }
        });
        if(this.options.open) this.show();
    };

    Drawer.prototype = {
        isShown: function(fully) {
            if(this.drawer !== null) {
                if(!fully)
                    return true;
                if(this.drawer.is(':visible'))
                    return true;
            }
            return false;
        },
        position: function() {
            var trigger = {
                offset: this.trigger.offset(),
                height: this.trigger.outerHeight(),
                width: this.trigger.outerWidth()
            };
            this.drawer.css({
                display: 'block',
                position: 'absolute'
            });
            switch(this.options.position) {
                case "right":
                case "left":
                    this.drawer.css(
                        'top',
                        (trigger.offset.top -
                         (this.drawer.outerHeight() / 2) +
                         (trigger.height / 2) +
                         this.options.offset[0]) + 'px');
                    break;
                case "top":
                case "top-right":
                case "top-left":
                    this.drawer.css(
                        'top',
                        (trigger.offset.top -
                         this.drawer.outerHeight() +
                         this.options.offset[0]) + 'px');
                    break;
                case "bottom":
                case "bottom-right":
                case "bottom-left":
                default:
                    this.drawer.css(
                        'top',
                        (trigger.offset.top + trigger.height +
                         this.options.offset[0]) + 'px');
                    break;
            }
            switch(this.options.position) {
                case "right":
                    this.drawer.css(
                        'left',
                        (trigger.offset.left +
                         trigger.width +
                         this.options.offset[1]) + 'px');
                    break;
                case "bottom-right":
                case "top-right":
                    this.drawer.css(
                        'left',
                        (trigger.offset.left +
                         this.options.offset[1]) + 'px');
                    break;
                case "left":
                    this.drawer.css(
                        'left',
                        (trigger.offset.left -
                         this.drawer.outerWidth() +
                         this.options.offset[1]) + 'px');
                    break;
                case "top-left":
                case "bottom-left":
                    this.drawer.css(
                        'left',
                        (trigger.offset.left -
                         this.drawer.outerWidth() +
                         trigger.width +
                         this.options.offset[1]) + 'px');
                    break;
                case "bottom":
                case "top":
                default:
                    this.drawer.css(
                        'left',
                        (trigger.offset.left -
                         (this.drawer.outerWidth() / 2) +
                         (trigger.width / 2) +
                         this.options.offset[1]) + 'px');
                    break;
            }
        },
        show: function() {
            var self = this;
            if(this.isShown()) this.hide();
            if(!this.options.remove && this.drawer !== null) {
                this.position();
            }
            else {
                var callback = function(content) {
                    var drawer = $(self.options.structure).
                        addClass(self.options.css_class).
                        css('display', 'none');
                    drawer.append(content);
                    self.drawer = drawer;
                    self.drawer.appendTo($('body'));
                    self.position();
                };
                if((typeof this.options.content === "string")) {
                    callback($(this.options.content).clone());
                }
                else {
                    this.options.content(callback, this);
                }
            }
        },
        hide: function() {
            if(this.drawer !== null) {
                if(this.options.remove) {
                    this.drawer.remove();
                    this.drawer = null;
                }
                else {
                    this.drawer.hide();
                }
            }
        }
    };

    $.fn.drawer = function() {
        var args = Array.prototype.slice.apply(arguments, []);
        return this.each(function() {
            var element = $(this);
            var drawer = element.data('drawer');
            if(!drawer) {
                if(args.length > 0)
                    drawer = new Drawer(this, args[0]);
                else
                    drawer = new Drawer(this);
                element.data('drawer', drawer);
            }
            else {
                if(args.length > 0)
                    drawer[args[0]].apply(drawer, args.slice(1));
            }
        });
    };
})(jQuery);
