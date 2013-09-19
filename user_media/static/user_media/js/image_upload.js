window.locale = {
    'fileupload': {
        'error': gettext('Error')
        ,'start': gettext('Start')
        ,'cancel': gettext('Cancel')
        ,'delete': gettext('Delete')
        ,'success': gettext('Successfully uploaded!')
    }
};

function initDeletion() {
    $('.galleryList .btn-danger').click(function() {
        var image = $(this).parents('.galleryList');
        // Get the modal content
        $.get($(this).attr('href'), function(data) {
            $('#deletionModal .modal-body').html(data).find('form').submit(function() {
                // If deletion form has been submitted, hide the modal and remove the image
                $('#deletionModal').modal('hide');
                image.hide();
                $.post($(this).attr('action'), $(this).serializeArray());
                return false;
            });
            $('#deletionModal').modal().modal('show');
        });
        return false;
    });
}

$(function () {
    $('#fileupload').each(function() {
        var form = $(this);
        form.fileupload({url: form.attr('action')});
        form.fileupload('option', {
            maxFileSize: 3000000
            ,acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i
            ,autoUpload: true
            ,sequentialUploads: true
        });
        form.bind('fileuploaddone', function (e, data) {
            // After upload add the image to the gallery list
            $('#galleryItems').append($.parseHTML(data.result.files[0].list_item_html)).show();
            $('.fileupload-buttonbar .text-danger').remove();
            setTimeout(function() {
                $('.template-download').fadeOut('slow').remove();
            }, 2000);
            initDeletion();
        });
        form.bind('fileuploadfail', function (e, data) {
            if ($('.fileupload-buttonbar .text-danger').length == 0) {
                $('.fileupload-buttonbar').append('<span class="text-danger"><small>' + data._response.jqXHR.responseText + '</small></span>');
            }
            setTimeout(function() {
                $('.template-download').fadeOut('slow').remove();
            }, 2000);
        });
    });

    // Prepare AJAX deletion
    initDeletion();
});