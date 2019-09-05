$('#audienceDetails').on('hide.bs.modal', function(e){
    $('#audienceDetails .modal-body table').html("");
});
$('#addAudience').on('hidden.bs.modal', function(e){
    $('#addAudience .modal-body table tbody').html("");
    $('#addAudience .modal-body table').css("display", "none");
    $('#searchBar').val('');
});
$('#searchBands').click(()=>{
    var bandName = $('#searchBar').val();
    url = window.location.origin + '/searchsimiliarbands/' + bandName;
    $.getJSON(url, function(data){
        // $('#addAudience .modal-body table tbody').html("");
        // $('#addAudience .modal-body table').css("display", "unset");
        // data.forEach(function(item){
        //     var tableCell = '<tr class="rowHover"><td>' + item.name + '</td><td>' + item.genres + '</td></tr>';
        //     $('#addAudience .modal-body table tbody').append(tableCell);
        // });
        console.log(data);
    })
})
$('#audienceDetails').on('show.bs.modal', function(e) {
    var audienceName = $(e.relatedTarget).data('id');
    url = window.location.origin + '/getAudienceDetails/' + audienceName;
    $.getJSON(url, function(data, status){
        data.forEach(function(item){
            var tableCell = '<tr><td>' + item.artist + '</td><td>' + item.genres + '</td><td>' + item.followers + '</td></tr>';
            $('#audienceDetails .modal-body table').append(tableCell);
        });
    });
});