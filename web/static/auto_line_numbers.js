;(function($){
	var AutoRowsNumbers = function (element, config){
	    this.$element = $(element);
	    this.$group = $('<div/>', { 'class': "textarea-group" });
	    this.$ol = $('<div/>', { 'class': 'textarea-rows' });
	    this.$wrap = $('<div/>', { 'class': 'textarea-wrap' });
	    this.$group.css({
	    	"width" : this.$element.outerWidth(true) + 'px',
	    	"display" : config.display
	    });
	    this.$ol.css({
	    	"color" : config.color,
	    	"width" : config.width,
	    	"height" : '100%',
	    	"font-size" : this.$element.css("font-size"),
	    	"line-height" : this.$element.css("line-height"),
	    	"position" : "absolute",
	    	"overflow" : "hidden",
	    	"margin" : 0,
			"padding" : 0,
            "border-right": "1px solid #ccc",
	    	"text-align": "center",
	    	"font-family" : this.$element.css("font-family")
	    });
	    this.$wrap.css({
	    	"padding" : ((this.$element.outerHeight() - this.$element.height())/2) + 'px 0',
	    	"background-color" : config.bgColor,
	    	"position" : "absolute",
	    	"box-sizing": "border-box",
            "margin": 0,
	    	"width" : config.width,
	    	"height" : '320px'
	    });
	    this.$element.css({
	    	"white-space" : "pre",
			"resize": "none",
			"color": "brown",
	    	"margin": 0,
			"box-sizing": "border-box",
            "padding-left" : (parseInt(config.width) -  parseInt(this.$element.css("border-left-width")) + parseInt(this.$element.css("padding-left"))) + 'px',
            "padding-right": "10px",
	    	"width": (this.$element.width() - parseInt(config.width)) + 'px'
		});
		this.$element.html(
			"print('hello share text')\n"
		)

	}

	AutoRowsNumbers.prototype = {
		constructor: AutoRowsNumbers,

		init : function(){
			var that = this;
			that.$element.wrap(that.$group);
			that.$ol.insertBefore(that.$element);
			this.$ol.wrap(that.$wrap)
			that.$element.on('keydown',{ that: that }, that.inputText);
			that.$element.on('scroll',{ that: that },that.syncScroll);
			that.inputText({data:{that:that}});
		},

		inputText: function(event){
			var that = event.data.that;

			setTimeout(function(){
				var value = that.$element.val();
				value.match(/\n/g) ? that.updateLine(value.match(/\n/g).length+1) : that.updateLine(1);
				that.syncScroll({data:{that:that}});
			},0);
		},

		updateLine: function(count){
			var that = this;
			that.$element;
			that.$ol.html('');

			var t = $(".share-text")[0];
			var boldLine = t.value.substr(0, t.selectionStart).split("\n").length;

			for(var i=1;i<=count;i++){
				if (i == boldLine){
					that.$ol.append("<div class='item-"+ i +" bold-text'>"+i+"</div>");
				}
				else{
					that.$ol.append("<div class='item-"+ i +"'>"+i+"</div>");
				}
			}
		},

		syncScroll: function(event){
			var that = event.data.that;
			that.$ol.children().eq(0).css("margin-top",  -(that.$element.scrollTop()+2) + "px");
		}
	}

	$.fn.setTextareaCount = function(option){
		var config = {};
		var option = arguments[0] ? arguments[0] : {};
		config.color = option.color ? option.color : "#FFF";
		config.width = option.width ? option.width : "30px";
		config.bgColor = option.bgColor ? option.bgColor : "#999";
		config.display = option.display ? option.display : "block";

	    return this.each(function () {
	      var $this = $(this),
	          data = $this.data('autoRowsNumbers');

	      if (!data){ $this.data('autoRowsNumbers', (data = new AutoRowsNumbers($this, config))); }

		  if (typeof option === 'string'){
	        return false;
	      } else {
	        data.init();
	      }
	    });
	}
})(jQuery)

$(document).ready(function() {
	$(".share-btn").bind("click", function() { 
		var text = $('.share-text').val();
		if (!text){
			return;
		}
		console.log(text, " text====")
		$.ajax({
			url: '/share/', 
			type: 'post',
			contentType: "application/json",
			data: JSON.stringify({
				content: text
			}),
			dataType: 'json',
			success: function(res){
				console.log(res, "====")
				var res = res;
				if (res.errcode == 0){
					window.location.href = 'http://127.0.0.1:5000/share/?code='+res.data;
				}else{
					alert('创建分享链接失败');
				}
			},
			fail: function(res){
				alert('创建分享链接失败');
			}
		});
	}); 
});
