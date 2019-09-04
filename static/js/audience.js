$('#audienceDetails').on('hide.bs.modal', function(e){
    $('#audienceDetails .modal-body table').html("")
});
$('#audienceDetails').on('show.bs.modal', function(e) {
    var audienceName = $(e.relatedTarget).data('id');
    url = window.location.origin + '/getAudienceDetails/' + audienceName;
    $.getJSON(url, function(data, status){
        data.forEach(function(item){
            var tableCell = '<tr><td>' + item.artist + '</td><td>' + item.genres + '</td><td>' + item.followers + '</td></tr>'
            $('#audienceDetails .modal-body table').append(tableCell)
        });
    });
});