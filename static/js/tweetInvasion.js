
localStorage.clear();
$('#beginInvasion').click(()=>{
    selectedContent = JSON.parse(localStorage.getItem('Content'));
    selectedAudience = JSON.parse(localStorage.getItem('Audience'));
    
    payload = {};
    payload['content'] = selectedContent;
    payload['audience'] = selectedAudience;
    payload = JSON.stringify(payload);

    url = window.location.origin + '/results';
    $.ajaxSetup({contentType:'application/json'});
    $.post(url, payload, function(data, status){
        if(data == 'success'){
            window.location.href = window.location.origin + '/beginInvasion';
        }
    });
})
$('.crowHover2, .arowHover2').click((e)=>{
    if(e.target.className == 'crowHover2'){
        label = 'Content';
        id = parseInt(e.target.dataset.id);
    }else{
        label = 'Audience';
    }
    temp = localStorage.getItem(label);
    if(temp == null){
        temp = [];
    }else{
        temp = JSON.parse(temp);
    }
    
    if(label == 'Content'){
        temp2 = {};
        temp2['id'] = id;
        temp2['name'] = e.target.innerHTML
        temp.push(temp2)
    }else{
        temp.push(e.target.innerHTML);
    }
    
    localStorage.setItem(label, JSON.stringify(temp));
    var tableCell = '<tr><td>' + e.target.innerHTML + '</td></tr>'
    repo = '#choose' + label + ' tbody';
    $(repo).append(tableCell);
});