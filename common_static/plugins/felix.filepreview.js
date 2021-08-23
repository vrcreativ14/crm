/**
 * https://github.com/zpalffy/preview-image-jquery 
 */
 (function($) {
	$.previewImage = function(options) {
	    var element = $(document);
	    var namespace = '.previewImage';

		var opts = $.extend({
			'xOffset': 220,    // the x offset from the cursor where the image will be overlayed.
			'yOffset': 0,   // the y offset from the cursor where the image will be overlayed.			
			'fadeIn': 'fast', // speed in ms to fade in, 'fast' and 'slow' also supported.
			'css': {          // css to use, may also be set to false.
				'padding': '5px',
				'border': '1px solid gray',
				'background-color': '#fff'
			},
			'eventSelector': '[data-preview-image]', // the selector for binding mouse events.
			'dataKey': 'previewImage', // the key to the link data, should match the above value.
			'overlayId': 'preview-image-plugin-overlay', // the id of the overlay that will be created.
		}, options);

		// unbind any previous event listeners:
		element.off(namespace);

		element.on('mouseover' + namespace, opts.eventSelector, function(e) {
			var f = $(this).data(opts.dataKey).split('/').pop().replace(/\#(.*?)$/, '').replace(/\?(.*?)$/, '');
			var x = f.split('.').pop().toLowerCase();
			var p = $('<p>').attr('id', opts.overlayId).css('position', 'absolute')
				.css('display', 'none');
				if($.inArray(x, ['jpg', 'png', 'gif', 'jpeg', 'bmp']) > -1)
					p.append($('<img>').attr('src', $(this).data(opts.dataKey)));
				else
					p.append($('<div class="no-preview"><i class="ti-layout-placeholder"></i>No preview available</div>'));

				p.append($('<div class="preview-file-name">' + $(this).data('title') + '</div>'));

			if (opts.css) p.css(opts.css);

			$('body').append(p);
			opts.yOffset = p.height();

			p.css("top", (e.pageY - opts.yOffset) + "px")
			 .css("left", (e.pageX - opts.xOffset) + "px")
			 .fadeIn(opts.fadeIn);
		});

		element.on('mouseout' + namespace, opts.eventSelector, function() {
			$('#' + opts.overlayId).remove();
		});

		element.on('mousemove' + namespace, opts.eventSelector, function(e) {
			$('#' + opts.overlayId).css("top", (e.pageY - opts.yOffset) + "px")
				.css("left", (e.pageX - opts.xOffset) + "px");
		});

		return this;
	};
})(jQuery);
