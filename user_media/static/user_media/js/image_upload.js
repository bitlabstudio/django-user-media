window.locale = {
    'fileupload': {
        'cancel': gettext('Cancel')
        ,'error': gettext('Ouch!')
        ,'success': gettext('Successful!')
    }
};

function initDeletion(body) {
    if (body.find('.fileinput-button input[multiple]').length > 0) {
        body.find('.userMediaImage .btn-danger').click(function() {
            var image = $(this).parents('.userMediaImage');
            // Get the modal content
            $.post($(this).attr('href'), {'csrfmiddlewaretoken': getCookie('csrftoken')}, function(data) {
                image.remove();
                checkImageContainer(body);
            });
            return false;
        });
    }
}

function checkImageContainer(body) {
    if (body.find('.fileinput-button input[multiple]').length > 0) {
        if (body.find('.userMediaImage').length == 0) {
            body.find('#positionContainer').hide();
            body.find('.userMediaImageUploaded img').attr('src', '/static/img/placeholder.jpg');
            body.find('.fileinput-button').removeAttr('disabled');
            body.find('#userMediaImageAmountInfo .text-danger').remove();
        } else {
            body.find('#positionContainer').show();
            body.find('.userMediaImageUploaded img').attr('src', $('.userMediaImage:visible').first().attr('data-thumbnail-large'));
            if (body.find('.userMediaImage:visible').length >= body.find('#userMediaImageMaximum').val()) {
                body.find('.fileinput-button').attr('disabled', 'disabled');
            } else {
                body.find('.fileinput-button').removeAttr('disabled');
                body.find('#userMediaImageAmountInfo .text-danger').remove();
            }
        }
    }
}

function initFileupload(objects, body) {
    if (!objects.hasClass('initialized')) {
        objects.addClass('initialized');
        objects.each(function() {
            var form = $(this);
            form.fileupload({url: form.attr('action')});
            form.fileupload('option', {
                maxFileSize: 3000000
                ,acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i
                ,autoUpload: true
                ,sequentialUploads: true
                ,filesContainer: '#userMediaImageProcess'
            });
            form.bind('fileuploaddone', function (e, data) {
                if ($('.fileinput-button input[multiple]').length > 0) {
                    // After upload add the image to the gallery list
                    body.find('#positionContainer').append($.parseHTML(data.result.files[0].list_item_html)).show();
                } else {
                    // If it's a single image, change the image src after upload
                    var extra_classes = body.find('.userMediaImageUploaded').attr('data-img-class');
                    var $new_image = $(data.result.files[0].list_item_html);
                    if (extra_classes) {
                        $new_image.addClass(extra_classes);
                    }
                    body.find('.userMediaImageUploaded img').replaceWith($new_image);
                }
                body.find('#userMediaImageAmountInfo .text-danger').remove();
                setTimeout(function() {
                    $('.template-download').fadeOut('slow').remove();
                }, 2000);
                initDeletion(body);
                checkImageContainer(body);
            });
            form.bind('fileuploadfail', function (e, data) {
                if (body.find('#userMediaImageAmountInfo .text-danger').length == 0 && data._response.jqXHR) {
                    body.find('#userMediaImageAmountInfo').append('<span class="text-danger"><small>' + data._response.jqXHR.responseText + '</small></span>');
                }
                setTimeout(function() {
                    body.find('.template-download').fadeOut('slow').remove();
                }, 2000);
            });
        });
        body.find('#positionContainer').on('sortupdate', function() {
            checkImageContainer(body);
        });
        checkImageContainer(body);

        // Prepare AJAX deletion
        initDeletion(body);
    }
}

$(document).on('DOMNodeInserted', function(e) {
    if ($(e.target).find('#fileupload, .multifileupload').length > 0) {
        initFileupload($(e.target).find('#fileupload, .multifileupload'), $(e.target));
    }
}).ready(function() {
    initFileupload($('#fileupload, .multifileupload'), $('body'));
});

function cropImage(identifier, path, url) {
    $('<img src="'+ path +'" alt="" />').load(function() {
        $(this).appendTo('#cropArea');
        var jcrop_api
            ,boundx
            ,boundy;

        $(this).Jcrop({aspectRatio: $('#cropRatio').val()}, function() {
            // Use the API to get the real image size
            var bounds = this.getBounds();
            boundx = bounds[0];
            boundy = bounds[1];
            // Store the API in the jcrop_api variable
            jcrop_api = this;
        });

        $('#cropSubmit').show().click(function() {
            $.post(url, $.extend(jcrop_api.tellSelect(), {'csrfmiddlewaretoken': getCookie('csrftoken')}), function(data) {
                $('#cropSubmit').unbind('click').hide();
                $('#cropArea').html('');
                $(identifier).find('img').attr('src', data);
            });
        });
    });
}
