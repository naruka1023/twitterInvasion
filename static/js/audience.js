
$('#audienceDetails').on('hidden.bs.modal', function(e){
    $('#audienceDetails .modal-body table tbody').html("");
});
$('#addAudience').on('hidden.bs.modal', function(e){
    $('#relatedTable tbody').html("");
    $('#tableContainer1').css("display", "none");
    $('#searchBar').val('');
});
$('#searchBands').click(()=>{
    var bandName = $('#searchBar').val();
    url = window.location.origin + '/searchsimiliarbands/' + bandName;
    $.getJSON(url, function(data){
        localStorage.setItem('relatedArtists', JSON.stringify(data));
        $('#relatedTable tbody').html("");
        $('#tableContainer1').css("display", "unset");
        data.forEach(function(item){
            var tableCell = '<tr  class="rowHover"><td data-id="'+ item.index +'" >' + item.name + '</td><td data-id="'+ item.index +'" >' + item.genres + '</td></tr>';
            $('#relatedTable tbody').append(tableCell);
        });
        $('.rowHover td').click((e)=>{
            var bandIndex = parseInt(e.target.dataset.id);
            bandDetails = localStorage.getItem('relatedArtists');
            bandDetails = JSON.parse(bandDetails)[bandIndex];

            if($('#chosenTable tbody').children().length == 0){
                chosenArray = [];
                chosenArray.push(bandDetails);
                localStorage.setItem('chosenArtists', JSON.stringify(chosenArray));
                console.log(chosenArray);
            }else{
                chosenArtists = localStorage.getItem('chosenArtists');
                chosenArtists = JSON.parse(chosenArtists);
                chosenArtists.push(bandDetails);
                localStorage.setItem('chosenArtists', JSON.stringify(chosenArtists));
                console.log(chosenArtists);
            }
            chosenTableCell = '<tr><td data-id="'+ bandDetails.index +'" >' + bandDetails.name + '</td><td data-id="'+ bandDetails.index +'" >' + bandDetails.genres + '</td></tr>';
            $('#chosenTable tbody').append(chosenTableCell);
        });
    })
})
function confirmClick(){
    chosenArtists = localStorage.getItem('chosenArtists');
    chosenArtists = JSON.parse(chosenArtists);
    payload ={};
    payload['artists'] = chosenArtists;
    payload['audienceName'] = $('#audienceNameInput').val();
    payload = JSON.stringify(payload);

    url = window.location.origin + '/addNewAudience';
    $.ajaxSetup({contentType:'application/json'});
    $.post(url, payload, function(data, status){
        if(data == 'success'){
            window.location.href = window.location.origin + '/audiences';
        }
    });
}
$('#audienceDetails').on('show.bs.modal', function(e) {
    var audienceName = $(e.relatedTarget).data('id');
    url = window.location.origin + '/getAudienceDetails/' + audienceName;
    $.getJSON(url, function(data, status){
        data.forEach(function(item){
            var tableCell = '<tr><td>' + item.artist + '</td><td>' + item.genres + '</td></tr>';
            $('#audienceDetails .modal-body table tbody').append(tableCell);
        });

    });
});