
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
        localStorage.setItem('relatedArtists', JSON.stringify(data));
        $('#addAudience .modal-body table tbody').html("");
        $('#addAudience .modal-body table').css("display", "unset");
        data.forEach(function(item){
            var tableCell = '<tr  class="rowHover"><td data-id="'+ item.index +'" >' + item.name + '</td><td data-id="'+ item.index +'" >' + item.genres + '</td><td style="display:none">' + item.id + '</td></tr>';
            $('#addAudience .modal-body table tbody').append(tableCell);
        });
        $('.rowHover td').click((e)=>{
            var bandIndex = parseInt(e.target.dataset.id);
            bandDetails = localStorage.getItem('relatedArtists');
            bandDetails = JSON.parse(bandDetails)[bandIndex]
            console.log(bandDetails);
        });
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