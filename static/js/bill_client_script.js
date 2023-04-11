let bill_no_select = document.getElementById('bill_no');
let client_name = document.getElementById('client_name');

bill_no_select.onload = function () {
    let bill_no = bill_no_select.value;
    fetch('/get_client_list/' + bill_no).then(function (response) {
        response.json().then(function (data) {
            let optionHTML = '';
            for (let client of data.client_list) {
                optionHTML += '<option value="' + client.client_id + '">' + client.client_name + '</option>'
            }
            client_name.innerHTML = optionHTML;
        });
    });
}

bill_no_select.onchange = function () {
    let bill_no = bill_no_select.value;
    fetch('/get_client_list/' + bill_no).then(function (response) {
        response.json().then(function (data) {
            let optionHTML = '';
            for (let client of data.client_list) {
                optionHTML += '<option value="' + client.client_id + '">' + client.client_name + '</option>'
            }
            client_name.innerHTML = optionHTML;
        });
    });
}

window.onload = function () {
    let bill_no = bill_no_select.value;
    let client = client_name.value;
    fetch('/get_client_list/' + bill_no).then(function (response) {
        response.json().then(function (data) {
            console.log(data)
            let optionHTML = '';
            for (let client of data.client_list) {
                optionHTML += '<option value="' + client.client_id + '">' + client.client_name + '</option>'
            }
            client_name.innerHTML = optionHTML;
        });
    });
}


